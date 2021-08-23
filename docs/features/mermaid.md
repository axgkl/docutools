# Mermaid Diagrams

See here for details: https://facelessuser.github.io/pymdown-extensions/extras/mermaid/

If you add this snippet (causing a download of mermaid.js from the Internet):


```
--8<--  
mermaid
--8<--  

```

and define conversion of custom fences in your mkdocs.yml like this:

```yaml
   - pymdownx.superfences:
       preserve_tabs: true
       custom_fences:
         - name: mermaid
           class: mermaid
           format: !!python/name:pymdownx.superfences.fence_code_format
 

```

Then you can define mermaid diagrams like this:

```

    ```mermaid
    graph TD
        A[Hard] -->|Text| B(Round)
        B --> C{Decision}
        C -->|One| D[Result 1]
        C -->|Two| E[Result 2]
    ```

```

## Diagram Types

!!! success "Practical"

    === "Sequence Diagrams"
        ```mermaid
        sequenceDiagram
            participant Alice
            participant Bob
            Alice->>John: Hello John, how are you?
            loop Healthcheck
                John->>John: Fight against hypochondria
            end
            Note right of John: Rational thoughts <br/>prevail!
            John-->>Alice: Great!
            John->>Bob: How about you?
            Bob-->>John: Jolly good!
        ```

    === "Flowcharts"
        ```mermaid
        graph TD
            A[Hard] -->|Text| B(Round)
            B --> C{Decision}
            C -->|One| D[Result 1]
            C -->|Two| E[Result 2]
        ```

    === "Class Diagrams"
        ```mermaid
        classDiagram
            Class01 <|-- AveryLongClass : Cool
            Class03 *-- Class04
            Class05 o-- Class06
            Class07 .. Class08
            Class09 --> C2 : Where am i?
            Class09 --* C3
            Class09 --|> Class07
            Class07 : equals()
            Class07 : Object[] elementData
            Class01 : size()
            Class01 : int chimp
            Class01 : int gorilla
            Class08 <--> C2: Cool label
        ```

    === "Entity Relationships"
        ```mermaid
        erDiagram
            CUSTOMER ||--o{ ORDER : places
            ORDER ||--|{ LINE-ITEM : contains
            CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
        ```

    === "State Diagrams"
        ```mermaid
        stateDiagram
            [*] --> First
            First --> Second
            First --> Third

            state First {
                [*] --> fir
                fir --> [*]
            }
            state Second {
                [*] --> sec
                sec --> [*]
            }
            state Third {
                [*] --> thi
                thi --> [*]
            }
        ```

!!! fail "Impractical"

    === "Git"
        Git diagrams are experimental and often don't render to a reasonable size. They overflow, but won't trigger
        scrollbars. They are the only diagram that often renders too large for the element they are assigned to.

        ```mermaid
        gitGraph:
        options
        {
            "nodeSpacing": 150,
            "nodeRadius": 10
        }
        end
        commit
        branch newbranch
        checkout newbranch
        commit
        commit
        checkout master
        commit
        commit
        merge newbranch
        ```

    === "Gantt"

        Gantt charts usually are too big to render properly in a page. If the element is big enough to hold it, and the
        chart is large, they render too small to see. If the element is not wide enough, the chart can sometimes render
        squished and hard to read.

        ```mermaid
        gantt
            dateFormat  YYYY-MM-DD
            title Adding GANTT diagram to mermaid
            excludes weekdays 2014-01-10

            section A section
            Completed task            :done,    des1, 2014-01-06,2014-01-08
            Active task               :active,  des2, 2014-01-09, 3d
            Future task               :         des3, after des2, 5d
            Future task2               :         des4, after des3, 5d
        ```

    === "Journey"

        Journey diagrams suffer from the same issues as Gantt charts. They just do not scale well and are often hard to
        read.

        ```mermaid
        journey
            title My working day
            section Go to work
              Make tea: 5: Me
              Go upstairs: 3: Me
              Do work: 1: Me, Cat
            section Go home
              Go downstairs: 5: Me
              Sit down: 5: Me
        ```

    === "Pie"

        Pie at times can seem to work great, but other times it can be hard to read or missing labels all together.
        Like the others in this list, it relates to sizing and scaling. For instance, if you were to view this on a
        mobile device, you'd likely see the key for the pie chart missing.

        ```mermaid
        pie
            title Key elements in Product X
            "Calcium" : 42.96
            "Potassium" : 50.05
            "Magnesium" : 10.01
            "Iron" :  5
        ```

## Source

    ```
        !!! success "Practical"

            === "Flowcharts"
                ```mermaid
                graph TD
                    A[Hard] -->|Text| B(Round)
                    B --> C{Decision}
                    C -->|One| D[Result 1]
                    C -->|Two| E[Result 2]
                ```

            === "Sequence Diagrams"
                ```mermaid
                sequenceDiagram
                    participant Alice
                    participant Bob
                    Alice->>John: Hello John, how are you?
                    loop Healthcheck
                        John->>John: Fight against hypochondria
                    end
                    Note right of John: Rational thoughts <br/>prevail!
                    John-->>Alice: Great!
                    John->>Bob: How about you?
                    Bob-->>John: Jolly good!
                ```

            === "Class Diagrams"
                ```mermaid
                classDiagram
                    Class01 <|-- AveryLongClass : Cool
                    Class03 *-- Class04
                    Class05 o-- Class06
                    Class07 .. Class08
                    Class09 --> C2 : Where am i?
                    Class09 --* C3
                    Class09 --|> Class07
                    Class07 : equals()
                    Class07 : Object[] elementData
                    Class01 : size()
                    Class01 : int chimp
                    Class01 : int gorilla
                    Class08 <--> C2: Cool label
                ```

            === "Entity Relationships"
                ```mermaid
                erDiagram
                    CUSTOMER ||--o{ ORDER : places
                    ORDER ||--|{ LINE-ITEM : contains
                    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
                ```

            === "State Diagrams"
                ```mermaid
                stateDiagram
                    [*] --> First
                    First --> Second
                    First --> Third

                    state First {
                        [*] --> fir
                        fir --> [*]
                    }
                    state Second {
                        [*] --> sec
                        sec --> [*]
                    }
                    state Third {
                        [*] --> thi
                        thi --> [*]
                    }
                ```

        !!! fail "Impractical"

            === "Git"
                Git diagrams are experimental and often don't render to a reasonable size. They overflow, but won't trigger
                scrollbars. They are the only diagram that often renders too large for the element they are assigned to.

                ```mermaid
                gitGraph:
                options
                {
                    "nodeSpacing": 150,
                    "nodeRadius": 10
                }
                end
                commit
                branch newbranch
                checkout newbranch
                commit
                commit
                checkout master
                commit
                commit
                merge newbranch
                ```

            === "Gantt"

                Gantt charts usually are too big to render properly in a page. If the element is big enough to hold it, and the
                chart is large, they render too small to see. If the element is not wide enough, the chart can sometimes render
                squished and hard to read.

                ```mermaid
                gantt
                    dateFormat  YYYY-MM-DD
                    title Adding GANTT diagram to mermaid
                    excludes weekdays 2014-01-10

                    section A section
                    Completed task            :done,    des1, 2014-01-06,2014-01-08
                    Active task               :active,  des2, 2014-01-09, 3d
                    Future task               :         des3, after des2, 5d
                    Future task2               :         des4, after des3, 5d
                ```

            === "Journey"

                Journey diagrams suffer from the same issues as Gantt charts. They just do not scale well and are often hard to
                read.

                ```mermaid
                journey
                    title My working day
                    section Go to work
                      Make tea: 5: Me
                      Go upstairs: 3: Me
                      Do work: 1: Me, Cat
                    section Go home
                      Go downstairs: 5: Me
                      Sit down: 5: Me
                ```

            === "Pie"

                Pie at times can seem to work great, but other times it can be hard to read or missing labels all together.
                Like the others in this list, it relates to sizing and scaling. For instance, if you were to view this on a
                mobile device, you'd likely see the key for the pie chart missing.

                ```mermaid
                pie
                    title Key elements in Product X
                    "Calcium" : 42.96
                    "Potassium" : 50.05
                    "Magnesium" : 10.01
                    "Iron" :  5
                ```


    ```


--8<--
mermaid
--8<--

