# news

### commit 1302-1574

A lot of things happened. Multiple new modes were added and i developed a new gameplay mechanism. Please check the commits for details, sry.

### commit 1203-1302

These commits were a bugfix code enhancement round.

* a code review was done
* reduced inline code
* splited methods
* removed old comments and commented out code
* fixed bugs
* moved more logic to the proper file
* simplified code and removed code redundancies
* reduced try excepts
* added more logging
* renamed variables/methods
* converted if to guarding ifs

I feel like the code quality gets better with these cleanup rounds, but new bugs get introduced while doing the cleanup and the amount of code that is marked as bad code do not get less. I take this as a sign that the code improves but there is still a lot to do while i judge the code harsher.

### commit 1100-1202

The commits were focused on making th save/load system work.

* some fixes for user-reported bugfixes (thanks for reporting the bugs)
* added submenus tho save system
* changed registry so no double instantiation happens
* handled splashscreen when saving
* added interaction for loading when starting the game
* fixed bugs resulting from the save system
* changed internal code structures to allow for serialization/saving
* extended use of the Saveable object
* saved more attributes for many things
* made story saveable
* added saving for characters and events

### commit 1000-1099

These commits were a bugfix/code enhancement round.

* placed game won screen at end of the working story line
* added Exceptions
* removed code redundancy primarily in movement code
* renamed things
* moved code to proper files
* removed commented out code
* reduced debug output and memory addresses in GUI
* converted some if/else to guards
* moved saving logic to saveing class
* fixed some crashes
* removed silly constants
* deleted old code
* fixed player being unable to exit quest menu when spawned from
* fixed dropping flask and picking it up again crash
* fixed drop quest not working in manual mode

The most annoying bugs are fixed and the game runs through most of the time. Crashes and memory addresses in GUI still happen though.

### commit 902-999

These commits were focused on adding more challenge to the game. I think i did pretty well. I still can beat the game, but i really have to try. Changes for adding challenge were:

* adding reputation cost for delegation quest to an subordinate
* added reputation cost for being impolite
* made many quest dispense no reward
* added reward/punishment for completing the tutorial in time
* added reward/punishment for doing the optional furnace intro
* added poisoned reward for asking people about things
* added time constraints to quests
* added punishment if time constraint for a quest is not honoured
* added ability to run people over with a mech
* added spawning more hoppers to steal the players job
* made player loose if there are more than 4 hoppers and player is the worst performer
* added military room that kills player when entered
* added reputation punishment for breaching military zones etc
* added kill squads to remove players not accepting the rules
* added prerequisites for chat options
* restricted actions and creatable quests to things the character was ordered in the past
* added quest for the player to kill himself, which actually happens if the player is in auto mode (intentional loophole to learn to kill somebody)
* removed life preservation quest if player is assigned vat duty
* added a moving roadblock to make learning paths harder
* made the collect scrap quest harder to solve
* added mice that appear under picked up items and knock characters unconscious
* added mice squatting rooms and killing anybody entering
* added punishment if subordinate dies
* moved the source of the cargo hauling quests including
* made the player acquire a floor permit before adventuring
* made most items bolted to the ground

other changes were:

* bugfixes
* military rooms
* more lister structures
* disabled skipping round on invisible rooms
* added ability to talk on terrain
* added ability to wake unconscious players

### commit 801-901

These commit were another cleanup round. It feels like the codebase got better, but there is still a lot of work to do. For example the save system still doesn't work reliably and lots of code is still marked as bad code.

* made callbacks savable
* fixed crashes
* made save system more abstract
* made callbacks savable
* reduced redundant code
* added saving for more details
* sourced lists of all items/quests from mapping
* fixed copy&paste fails
* moved more code to saveing
* fixed bugs
* removed debug code from GUI
* removed dead code

I made progress, but clean up rounds will need to happen periodically.

### commit 701-800

The sole focus of theses commits was to create a system to save and load the gamestate with. This was successful in implementing a system for saving the game but was not successful in creating a reliable save/load function. A saving/loading system exist for every important part of the game, but the game crashes a lot during saving/loading because many of the getters/setter for the specific instances and subtypes are missing.

The main changes are:

* saving/loading of characters
* saving/loading of items
* saving/loading of rooms
* saving/loading of cinematics
* saving/loading of events
* saving/loading of chat options
* added a system to create unique ids for everything
* added tracking of the creator of everything including a void object for thing created out of the blue
* added a mechanism to reduce the savestate to the difference from initial generation to current state
* added a mechanism to serialize function calls
* moved chats to a chat file

Since the core mechanics for saving/loading exists there was good progress, but a new clean up round is needed to fix all the bad code introduced and to fix the crashes resulting from this feature.

### commit 609-700

The main focus was to eliminate bugs and to clean up the code. Tasks completed are:

* commented the whole codebase
* removed debug output from gui
* fixed typos
* removed useless / dead / commented out code
* removed most of the non meta quest based quests
* reduced number of inline functions
* added deregistering for listeners resulting in better performance, less bugs and hopefully less memory bloat
* converted story sections from step to step instructions to quests
* bugfixes
* reordered/reformated code
* added unconscious state
* made the growth tank actually dispense unconscious bodies
* added categories for listening to reduce spam and to allowing quest to listen for actions
* made a container quest for the tutorial questions to prepare proper npc spawning

I made good progress but i will need another cleanup later.

### commit 500-608

The main focus was to make the basic game mechanic visible and understandable and failed to do so. I made the following changes

* forced the player to talk to npc at least a bit
* added chat options hinting at and explaining the automode
* added interaction options to the quest menu
* added more quests and options to the advanced quest menu
* added npc that compete with the player for quests
* added a longish period of repetitive quest to coerce the player into using auto mode
* added a big quest that the player has to delegate to NPCs. This is kind of broken.

I made some progress but i kind of failed and there is a lot of work left to do. I hade some people test play the game and getting sidetracked by the issues uncovered and features requested. Notable changes and features added are:

* lot of bugfixes
* added a list of music as a baseline for discussions on how game music should be like. The music can (i think) be put into the game legally. [LIST](technicalConcepts/music)
* added 2 additional terrains. The can only be accessed by using the -T (scrapYard,nothingness) parameter and pretty much broken at this point of time.
* added various dialog
* added dialog pictures explaining how to move
* added a scrolling bar at the bottom of the screen explaining the display characters and the command chars
* tweaked turorialroom
* added a perspective rendered mode. It is still incomplete
* added a crude debug menu

### commit 400-500

The main focus was to solve the missing feeling of purpose, progress, adventure and discovery. I wrote all commits by myself, so this will reflect my perspective only.

I think i created a feeling of

* purpose, by adding hints on what comes after the current phase and the obvious expectation that the player will try to get into the next phase. This is kind of weak, but works well enough for now and can be scaled up. Additional elements of purpose would be great to have.
* progress, by adding chat menus, quests and story phases that have to be unlocked by the player and congratulating the player when a new thing is unlocked. There are only a few things to unlock and the way to get there is pretty grindy, but that can be improved on.
* adventure, by allowing the player to progress, to talk to people, learn some lore and be send through the mech the player doesn't fully know the purpose of. Also some mild element of danger and punishment is added to stress the player a bit. This topic is barely scratched, but i think a combination of the feeling of purpose, progress and discovery will likely create a feeling of adventure.
* discovery, by putting the player into a small room and having the player discover more of the map combined with bits of lore after some progress. Giving the player free movement allows to find some easter egg like functionality that is not bound into the story yet. This should cover both the players that rush for completion and the players who like to look around something to find. I think the way to go is revealing more features/lore/areas as the player progresses combined with experimental stuff that's harder to find.

All in all i think i figured out a way to make the game feel like a game and hope that continuing this way will make the game feel like a interesting game further down the line.

I did not only work on the issues above. Other notable changes and features that were added are:

* many bugfixes
* added chat options that spawn story phases that spawn quests that spawn chat options and other combinations of these things. This is intended to test the waters on a fully dynamic system in this regard.
* added a autocompletion mechanism to the whole story and all quests used in the story. This means basically everything the player does now can be reused to have NPCs running around doing these things. Also this is a preparation to give the player the ability to command NPCs to complete quests like these as a way to exercise power.
* rebuild many of the quests in a recursive quest structure, that can get quite complex. This is partially intended, but needs to be scaled to not appear ridiculous. Also this is a preparation to have everybody do only one quest and have the rest as a subquest.
* added some elements of a economy, by adding the possibility to produce some items from scrap and by added a half working construction site. This is not embedded into the world in a meaningful way, but i think it is notable since it's a small step into the direction of an economy.
* A reputation system was added to be able to unlock stuff. This only notable since it is not intended to be kept on the long run, so don't get attached to it.
* added npc specific dialog options to test the waters for a proper dynamic chat system.
* the ability to download and play CC songs to have some background music. This is more a symbolic thing, since it's using mplayer and only plays 2 songs.
* a half working tile based display mode based on pygame
* added quest queues and quest dispensers. These are not really used yet, but these are intended to allow to task quests without caring whom to task with the quest exactly
* added more quests. For example a quest to murder people which surely will be useful later
* added some more rooms.

### commit 0-400

unicode issues are resolved by having a almost pure ASCII renderer as default. Unicode modes can still be configured and can be toggled while playing using '`' (default). This means the game is almost cross platform supporting linux and mac.
