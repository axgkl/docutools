#!/usr/bin/env python
"""
Literate Programming / Language of Babel style

Edit: We support this now not only from emacs but also from normal mkdocs markdown.
See the documentation.



Old emacs centric docs follow:

Org Mode / Mkdocs Helper Script. 

Usage: See e.g. repos/lc/docs/.../getting_started.org

Basics: 
    In you org file have this:


#+BEGIN_SRC python :exports none :results silent :session pyroot
from sys import modules as m; m.pop('lp') if 'lp' in m else 0; import lp
#lp.alias('lcm', '$d_repos/lc/build/make')
run = lp.p(lp.run, fmt='mk_cmd_out', cache='getting_started')
root = lp.p(run, root=True)
#+END_SRC

which you execute at any change of the module (reloads)

Set this:

:PROPERTIES:
:header-args:python: :session pyroot :exports results :results html
:END:

Then using is like

#+BEGIN_SRC python
root([
      {
        'cmd': 'm -l run lnr -d',
        'expect': '\n/opt/repos/lc/node-red#',
        'timeout': 15,
      },
      {
        'cmd': "ax/start -p ''",
        'expect': 'Started flows',
        'timeout': 10,
        'cmt': "-p '': no project"
      },
      ], new_session='root_nr')
#+END_SRC


You can invoke the methods also from here, via __main__
"""

import subprocess as sp
import string
import hashlib
import os
import json
from functools import partial as p
from ast import literal_eval
import time

env = os.environ
wait = time.sleep
now = time.time
exists = os.path.exists
user = env['USER']
d_cache = '/tmp/lp_py_cache_files_%s/' % user
env['PATH'] = 'bin:%s' % env.get('PATH', '')

cfg = {}
mk_console = '''
```%(lang)s
%(cmd)s
%(res)s
```
'''

# seems we don't need the stupid dot anymore for the javascript xterm part (?)
# mk_cmd_out = '''

# === "Cmd"

#     ```console
#     %(cmds)s
#     ```

#     .

# === "Output"

#     %(ress)s

# '''


mk_cmd_out = '''

=== "Cmd"
    
    ```console
    %(cmds)s
    ```

=== "Output"

    %(ress)s

'''


class mk_cmd_out_fetch:
    org = '''


#+begin_tab:Command

#+BEGIN_SRC console :eval no

%(cmds)s

#+END_SRC

#+end_tab:Command


#+begin_tab:Output

%(ress)s

#+end_tab:Output

'''
    mkdocs = mk_cmd_out


xt_flat = '''
<xterm %(root)s/>

    %(ress)s

'''

xt_flat_fetch = '''
    <xterm />

         remote_content

    ![](%(fn_frm)s)
'''


# xt_flat_fetch_test = """
##+begin_tab:foo

#    <xtf %(root)s xtfrm=file:%(fn_frm)s></xtf>

##+end_tab:foo
# """

# this not yet sane:
##+begin_tab:foo

#    <xterm></xterm>

#        ansiremotecontent

#    [ ](file:./images/info_flow_adm.ansi)

##+end_tab:foo


dflt_fmt = 'mk_cmd_out'
aliases = {}
to_list = lambda s: s if isinstance(s, list) else [s]

last_result = [None]
last_ansi_file = [None]


def repl_dollar_var_with_env_val(s, die_on_fail=True):
    if not '$' in s:
        return s
    for k in env:
        if k in s:
            s = s.replace('$' + k, env[k])
    if '$' in s:
        print('Not defined in environ: $%s' % s)
    return s


def spresc(cmd):
    """subprocess run - with escape sequences escaped (for tmux)"""
    return sprun(cmd.encode('unicode-escape'))


def sprun(*a, **kw):
    """Running a command as subprocess"""
    print('--> ', a, kw)  # for the user (also in view messages)
    return p(sp.check_output, shell=True, stderr=sp.STDOUT)(*a, **kw)


class T:
    def xt_flat(resl, **kw):
        add_cmd = kw.get('add_cmd', True)
        root = '' if not kw.get('root') else 'root'
        r = []
        for cr in resl:
            cmdstr, res = get_cmd(cr), cr.get('res')
            if add_cmd and not cmdstr in res:
                res = cmdstr + '\n' + res
            r.append(res)
        ress = '\n'.join(r)
        fetch = kw.get('fetch')
        if fetch:
            fn_frm = kw['fn_frm'] = file_.write_fetchable(ress, **kw)
            t = xt_flat_fetch
            ress = t % locals()
        else:
            ress = ress.replace('\n', '\n    ')
            ress = xt_flat % locals()
        return ress

    def mk_cmd_out(res, **kw):
        root = '' if not kw.get('root') else 'root'

        def add_prompt(c, r):
            """We don't do it since console rendering requires $ or # only for syn hilite"""
            c, cmd = (c.get('cmd'), c) if isinstance(c, dict) else (c, {'cmd': c})
            if c:
                p = '#' if root else '$'
                c = '%s %s' % (p, c)
                cmt = cmd.get('cmt')
                if cmt:
                    if len(c) + len(cmt) > 80:
                        c = '%s # %s:\n%s' % (p, cmt, c)
                    else:
                        c = '%s # %s' % (c, cmt)
            return {'cmdstr': c, 'cmd': cmd, 'res': r}

        ress = T.xt_flat(res, add_cmd=kw.pop('add_cmd', False), **kw)
        res = [add_prompt(m.get('cmd'), m['res']) for m in res]
        if not any([True for m in res if m['cmdstr']]):
            return ress
        cmds = '\n'.join([r['cmdstr'] for r in res if r.get('cmdstr')])
        fetch = kw.get('fetch')
        if fetch:
            t = getattr(mk_cmd_out_fetch, kw['fetched_block_fmt'])
            r = t % locals()
        else:
            # indent one in:
            cmds = cmds.replace('\n', '\n    ')
            ress = ress.replace('\n', '\n    ')
            r = mk_cmd_out % locals()
        return r

    def mk_console(res, root=False, **kw):
        resl = res
        r = []
        lang = kw.get('lang', 'console')
        for res in resl:
            p = ''
            if lang in ['bash', 'sh']:
                p = '# ' if kw.get('root') else '$ '
            cmd = p + get_cmd(res)
            res = res['res']
            # is the command part of the res? then skip print:
            if cmd.strip() == res.strip().split('\n', 1)[0].strip():
                cmd = 'SKIP-PRINT-OUT'
            r.append(mk_console % locals())

        r = ('\n'.join(r)).splitlines()
        r = [l for l in r if not 'SKIP-PRINT-OUT' in l]
        return '\n'.join(r)


T.xtf = T.xt_flat


def get_cmd(res):
    cmd = res.get('cmd', '')
    return get_cmd(cmd) if isinstance(cmd, dict) else cmd


def alias(k, v):
    aliases[k + ' '] = v + ' '


def fmt(res, **kw):
    res = to_list(res)
    for c in res:
        c['res'] = c['res'].replace('\n```', '\n ``')
        if kw.get('hide_cmd'):
            c['cmd'] = ''

    fmt = kw.get('fmt', dflt_fmt)
    fmt = getattr(T, fmt)
    return fmt(res, **kw)


letters = string.ascii_letters + string.digits + '_'


class cache:
    """result cache, delete files or don't supply for fast execution"""

    def fn(cmd, kw):
        key = kw.get('cache')
        if not key:
            return
        s = str(cmd)
        h = hashlib.md5(s.encode('utf-8')).hexdigest()
        s = s.replace(' ', '_').replace(':', '_')
        s = ''.join([c for c in s if c in letters])
        d = d_cache + key
        os.makedirs(d, exist_ok=True)
        fn = '%s/%s_%s' % (d, s[:30], h)
        kw['fn_cache'] = fn
        return fn

    def get(cmd, kw):
        fn = cache.fn(cmd, kw)
        if not fn:
            return
        if exists(fn):
            with open(fn, 'r') as fd:
                return fd.read()

    def add(cmd, res, kw):
        fn = kw.get('fn_cache')
        if fn:
            with open(fn, 'w') as fd:
                fd.write(str(res))


def init_prompt(n):
    """run before each command"""
    # -R reset terminal state:
    sprun('tmux send-keys -R -t %s:1' % n)
    # if not mode == 'python':
    #     sprun('tmux send-keys -t %s:1 "clear" Enter' % n)
    #     while b'clear' in sprun('tmux capture-pane -ep -t %s:1' % n):
    #         wait(0.05)
    # else:
    #     pass
    #     # sprun('tmux send-keys -t %s:1 "%s" Enter' % (n, begin_cmd))

    sprun('tmux clear-history -t %s:1' % n)
    sprun("tmux send-keys -t %s:1 '' Enter" % n)


class session:
    def get(session_name, **kw):
        """
        Starts tmux if not running and delivers a srun_in_tmux function,
        parametrized for that session.
        """
        s = '\n' + os.popen('tmux ls').read()
        if not '\n%s:' % session_name in s:
            # new session:
            s = session_name
            # path is set new. bash (if executing user's shell is fish we'd be screwed)
            sprun('export SHELL=/bin/bash; export p="$PATH"; tmux new -s %s -d' % s)
            a = 'tmux send-keys -t %(session)s:1 \'export PATH="$p"; export PS1="%(prompt)s" \' Enter'
            b = {'prompt': kw.get('prompt', '$ '), 'session': s}
            for i in (1, 2):
                try:
                    sprun(a % b)
                    # the reset in init prompt needs thate time before
                    # otherwise you have the command 2 times in
                    time.sleep(0.2)
                    break
                except Exception as ex:
                    # on new systems it maybe just missing and the user / runner does not caser. Lets do it:
                    fn = env.get('HOME', '') + '/.tmux.conf'
                    if not exists(fn) and i == 1:
                        print('!! Writing %s to set base index to 1 !!' % fn)
                        r = 'set-option -g base-index 1\nset-window-option -g pane-base-index 1\n'
                        with open(fn, 'w') as fd:
                            fd.write(r)
                        continue
                    # everybody has 1 and its a mess to detect or change
                    raise Exception(
                        (
                            'tmux session start failed. Do you have tmux, '
                            'configured with base index 1? 0 is default but will NOT work!!'
                        )
                    )
            init_prompt(s)
            if kw.get('root'):
                sprun('tmux send-keys -t %s "sudo bash" Enter' % s)
                wait(0.1)

        res = p(session.srun_in_tmux, session_name=session_name)
        return res

    def srun(cmds, session_name, **kw):
        S = session.get(session_name, **kw)
        if kw.get('with_paths'):
            for e in 'PATH', 'PYTHONPATH':
                S('export %s="%s"' % (e, os.environ.get(e, '')), **kw)
        res = [{'cmd': cmd, 'res': S(cmd, **kw)} for cmd in to_list(cmds)]
        res = [i for i in res if not i.get('res') == 'silent']  # sleeps removed
        if kw.get('kill_session'):
            session.kill(session_name)
        return res

    def srun_in_tmux(cmd, session_name, expect=None, timeout=1, **kw):
        n = session_name

        # TODO: clean up

        assert_ = kw.get('assert')
        silent = kw.get('silent')
        if isinstance(cmd, dict):
            timeout = cmd.get('timeout', timeout)
            expect = cmd.get('expect', expect)
            assert_ = cmd.get('assert', assert_)
            silent = cmd.get('silent', silent)
            cmd = cmd.get('cmd')  # if not given: only produce output
        if cmd.startswith('wait '):
            time.sleep(float(cmd.split()[1]))
            return 'silent'

        sk = 'send-keys:'
        if cmd.startswith('send-keys:'):
            spresc('tmux send-keys -t %s:1 %s' % (n, cmd.split(sk, 1)[1].strip()))
            return 'silent'

        expect_echo_out_cmd = ''
        if expect is None:
            # not match on the issuing cmd
            expect_echo_out_cmd = ';echo -n ax_; echo -n done'
            cmd += expect_echo_out_cmd
            expect = 'ax_done'
        if expect is False:
            expectb = b'sollte nie vorkommen, we want timeout'
        else:
            expectb = expect.encode('utf-8')
        if cmd:
            init_prompt(n)
            spresc("tmux send-keys -t %s:1 '%s' Enter" % (n, cmd))
        t0 = now()
        wait_dt = 0.1
        while True:
            res = sprun('tmux capture-pane -epJS -1000000 -t %s:1' % n)
            if expectb in res:
                break
            if now() - t0 > timeout:
                if expect is False:
                    # wanted then:
                    break
                raise Exception(
                    'Command %s: Timeout (> %s sec) expecting "%s"'
                    % (cmd, timeout, expectb.decode('utf-8'))
                )
            wait(wait_dt)  # fast first
            wait_dt = timeout / 10.0
        res = res.decode('utf-8')
        if expect_echo_out_cmd:
            # when expect was given we include it (expect="Ready to accept Connections")
            # expect_echo_out_cmd is empty then
            res = res.split(expect, 1)[0].strip()
            res = res.replace(expect_echo_out_cmd, '')
        else:
            # the tmux window contains a lot of white space after the last output when short cmd
            res = res.strip()
        if assert_ is not None:
            if not assert_ in res:
                msg = (
                    'Assertion failed: Expected string "%s" not found in result (\n%s)'
                )
                raise Exception(msg % (assert_, res,))

        print('----------')
        print(res)
        print('----------')
        return res if not silent else 'silent'

    def find_output_range(res, between, ls=b'\n'):
        """default: parse out last range in res between begin and end of between"""
        # todo: regex
        pre, post = res.rsplit(between[0], 1)
        r = pre.rsplit(ls, 1)[-1] + between[0]
        body, post = post.split(between[1], 1)
        r += body
        r += between[1] + post.split(ls, 1)[0]
        return r

    def kill(session_name):
        os.system('tmux kill-session -t %s' % session_name)


def pb(s):
    try:
        s = s.decode('utf-8')
    except Exception as ex:
        pass
    print(s)


def get_args(*a, **kw):
    return {'args': a, 'kw': kw}


def clear_cache():
    os.system('rm -rf "%s"' % d_cache)


def root(cmd, **kw):
    return run(cmd, root=True, **kw)


def flog(*s):
    with open('/tmp/lpcache_%s' % user, 'a') as fd:
        fd.write(str(s))
        fd.write('\n')


flog(os.getcwd())


class file_:
    def create(kw):
        fn = kw['fn']
        c = kw['content']
        if kw.get('lang') in ('js', 'javascript', 'json'):
            if isinstance(c, (dict, list, tuple)):
                c = json.dumps(c, indent=4)
        with open(fn, 'w') as fd:
            fd.write(str(c))
        os.system('chmod %s %s' % (kw.get('chmod', 660), fn))
        return file_.show(kw)

    def show(kw):
        fn = kw['fn']
        with open(fn, 'r') as fd:
            c = fd.read()
        res = {'cmd': 'cat %s' % fn, 'res': c}
        if kw.get('lang') not in ['sh', 'bash']:
            res['cmd'] = '$ ' + res['cmd']
        return res

    def write_fetchable(cont, fetch, **kw):
        """write .ansi XTF files"""
        d, fn = kw['fn_doc'].rsplit('/', 1)
        lnk = '/images/%s_%s.ansi' % (fn, fetch)
        fn = d + lnk
        if not exists(d + '/images'):
            os.makedirs(d + '/images')
        with open(fn, 'w') as fd:
            fd.write(rpl(cont, kw))
        last_ansi_file[0] = fn
        return '.' + lnk


def env_cmds(kw, when):
    cmd = kw.get(when)
    if cmd:
        if os.system(cmd):
            raise Exception('%s run failed: %s. kw: %s' % (when, cmd, str(kw)))


import sys
from io import StringIO


def run_as_python(cmd, kw):
    """
    interpret the command as python:
    no session, lang = python:
    """
    kw['fmt'] = kw.get('fmt', 'mk_console')
    h = sys.stdout
    # when a breakpoint is in a python block redirection sucks, user wants to debug:
    # TODO: write cmd to a file for better debugging
    redir = True if not 'breakpoint()' in cmd else False
    if redir:
        sys.stdout = StringIO()
    else:
        msg = '"breakpoint()" found -> not redir stdout. Result will be this message'
        print(msg)
        res = msg
    try:
        exec(cmd, {'ctx': kw})
    except Exception as ex:
        if redir:
            sys.stdout = h

    finally:
        if redir:
            try:
                res = sys.stdout.getvalue()
            except AttributeError as ex:
                res = ''  # nothing printed
            sys.stdout = h
    return {'cmd': cmd, 'res': res}


def rpl(s, kw):
    'global replacement'
    rpl = kw.get('rpl')
    if rpl:
        if not isinstance(rpl[0], (list, tuple)):
            rpl = [rpl]
        for r in rpl:
            s = s.replace(r[0], r[1])
    return s


def repl_dollar_var_with_env_vals(kw, *keys):
    for k in keys:
        v = kw.get(k)
        if v:
            kw[k] = repl_dollar_var_with_env_val(v)


def multi_line_to_list(cmd):
    if not isinstance(cmd, str):
        return cmd
    try:
        l = cmd.split('\n')
    except Exception as ex:
        print('breakpoint set')
        breakpoint()
        keep_ctx = True
    if len(l) == len([i for i in l if not i.startswith(' ')]):
        return l
    return cmd


def run(cmd, dt_cache=1, nocache=False, fn_doc=None, **kw):
    """
    dt_cache: Only cache when runtime is greater than this:
    rpl: global post run replacement
    fn_doc: required: location of source file (async flow links contain its name)
    """
    repl_dollar_var_with_env_vals(kw, 'fn', 'cwd')
    # you could set this to org:
    kw['fetched_block_fmt'] = kw.get('fetched_block_fmt', 'mkdocs')

    assert fn_doc, 'fn_doc run argument missing'
    kw['fn_doc'] = os.path.abspath(fn_doc)
    t0 = now()
    cached = cache.get(cmd, kw)
    if cached and not nocache and not env.get('disable_lp_cache'):
        return cached
    env_cmds(kw, 'cmd_prepare')

    cwd = kw.get('cwd')
    if cwd:
        here = os.getcwd()
        os.chdir(cwd)

    # mode = kw.get('xmode')
    # # in python we need tmux session (to start python first):
    # if not kw.get('session') and mode == 'python':
    #     kw['session'] = mode
    ns = kw.pop('new_session', None)
    if ns in (True, False):
        raise Exception(
            'Variable new_session must be string (the name of a session which is guaranteed a new one)'
        )
    if ns:
        session.kill(ns)
        kw['session'] = ns
    mode = kw.get('mode')
    if mode in (None, 'bash', 'ls'):
        cmd = multi_line_to_list(cmd)

    session_name = kw.pop('session', 0)
    if session_name:
        res = session.srun(cmd, session_name=session_name, **kw)
        if cwd:
            os.chdir(here)

    elif mode == 'python':
        res = run_as_python(cmd, kw)

    elif mode == 'make_file':
        kw['content'] = cmd
        kw['fmt'] = kw.get('fmt', 'mk_console')
        res = file_.create(kw)

    elif mode == 'show_file':
        kw['fmt'] = kw.get('fmt', 'mk_console')
        res = file_.show(kw)

    else:
        # os.system style:
        if not isinstance(cmd, list):
            cmd = [cmd]

        res = []
        for c in cmd:
            c1 = c['cmd'] if isinstance(c, dict) else c
            rcmd = c1
            prompt = '$'
            if kw.get('root'):
                rcmd = 'sudo %s' % rcmd
                rcmd = rcmd.replace(' && ', ' && sudo ')
                prompt = '#'
            for k, v in aliases.items():
                rcmd = rcmd.replace(k, v)

            # return sp.check_output(['sudo podman ps -a'], shell=True)
            r = sprun(rcmd)
            r = r.decode('utf-8').rstrip()
            r = ''.join([prompt, ' ', c1, '\n', r])
            # res = '%s %s\n' % (prompt, cmd) + res

            res.append({'cmd': c1, 'res': r})

    # cwd header only for the current block:
    if cwd:
        os.chdir(here)

    if not kw.get('silent'):
        res = fmt(res, **kw)
        res = rpl(res, kw)
    else:
        res = ''

    # only cache slow stuffs:
    # if now() - t0 > dt_cache:
    cache.add(cmd, res, kw)
    last_result[0] = res
    return res


def test():
    """Better use docutools lp_client to test"""
    print(
        run(
            'cat "$HOME/bin/xdg-mime"',
            fmt='mk_cmd_out',
            fetch='program_verb2',
            fn_doc='/tmp/foo.org',
        )
    )
    return

    print(
        run('ls -lta', fmt='mk_cmd_out', fetch='program_verb2', fn_doc='/tmp/foo.org')
    )
    return
    print(run('m info', fetch='info', fn_doc='/tmp/foo.org'))
    return
    print(run('cat /usr/local/bin/m', fmt='mk_console'))
    return
    res = run({'expect': ['H: register', 'status'], 'timeout': 15,}, session='root_py')
    print(res)
    return
    run(
        [
            {
                'cmd': "m -l run lp -d -c 'echo \$CONTAINER_VER' 2>/dev/null",
                'cmt': 'version check - it is set as env var within',
                'timeout': 5,
            }
        ],
        new_session='root_py',
        fmt='mk_cmd_out',
    )
    return

    print(
        root(
            [
                {'cmd': 'm registry_login', 'cmt': 'foo'},
                'm -l pull lnr',
                'm -l pull lp',
            ],
            new_session='root',
            cache='foo',
        )
    )
    return

    print(
        run(
            [
                'm run -h',
                {
                    'cmd': 'm -l run lnr -Dd',
                    'expect': '\n/opt/repos/lc/node-red#',
                    'timeout': 10,
                },
                'ax/start -p false',
            ],
            new_session='root_nr',
            root=True,
        )
    )

    run('m registry_login && m -l pull lnr && m -l pull lp', root=True)
    # run(['sudo ls -lta /', 'bash', 'whoami', 'ls -lta /'], new_session='bar')


if __name__ == '__main__':
    test()