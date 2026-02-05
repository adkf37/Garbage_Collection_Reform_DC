Problem Statement: DC's garbage collection system is inefficient. 

Background: The system is built on each property (up to 3 units?) being assigned 1 to 3 garbage cans and 1 to 3 recycling cans. Each can is set out on collection days and picked up by garbage trucks staffed by at least one collector, usually 2, and one driver.

Hypothesis: Moving toward a shared container system would:

- make the system more efficient
- allow for more granular recycling streams (cardboard + aluminum, instead of putting everything in one stream)
- make the City cleaner by having garbage collection bins les susceptible to rats and having fewer (but larger bins)
- make trash capacity more flexible because you can add capacity simmply by picking up the containers more often

Plan Outline: Genrally, the City would station large public containers (think small dumpster) in 2 or 3 places per block. City residents would take their garbage, recycling, and compost to these large public containers. For collection, this would elmiinate the need for collectors and move to a more automated system with just a driver responsible for collecting the waste from the bins, using an electronic lift mounted to the truck.

Requirements: 

- One of the key requirements is that we have to have a limit on how far people would have to walk from there residence. I think we could investigate 250, 500, and 750 ft distances to start. 
- We need to make sure that the system has a lot of trash capcaity. let's match what is currently being collected, but also model what happens if the city's population grows by 25%
- Consider where this collection scheme could be difficult given geogrpahy of roads and tree cover.

Output Goals:

- Write-up in Markdown/Quarto/Latex with interactive versions of the elements described below
- Interactive map of bins
    - Map should allow anybody to enter a DC address and see where their nearest bin would be.
- Calculate:
    - Startup cost of new sytem
        - New trucks
        - New bins
        - Collecting old bins
    - Operating cost of new system
    - Parking spaces consumed by bins
    - Trash capacity based on different collection frequencies


Data Sources:

- Map of DC

Background Research

- What we're proposing is adopting Barcelona's waste collection system. Let's research analysis of this system for evidence that it is more efficient and makes the city cleaner.