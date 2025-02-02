# Advanced-GTA-SA-IDE-File-Editor

- Scan the selected folder for every ID file , loads all of those files into the editor with a single ediable window that is no need to change tabs (seemless scrolling between files) 
- Search function search through all ide files in a single go , you can easily look for duplicates like that or navigate
- Side IDE list shows every IDE file loaded , you can navigate between IDE blocks insanely fast using it
- Make ANY change in the editor window and it will detect the change made in the particular IDE file and will the update the change in the original file accordingly once you save the changes
- The TOOLS section has some interesting stuff :
    - Generation of Brief Decription of the IDE files opened in editor which includeds , type of ide file , ID range of ide file (maybe bugged for few ide files) , Total no of entries
    - The generated file also shows all the unused ids between 0-90000 (well i was lazy to make upper limit customizable so put a number which will works for all) at the end of file
    - IDE IDs Renumberer , pretty self explanatory name
          - there are two modes : Batch and Individual
               - in batch mode it takes single input for id_start and it start renumbering from first file to end of last file (ids are continuous)
               - in individual mode you get to set id_start of every single IDE file
    - IPL LOD Separator - This tool processes IPL files by extracting LOD models entries from inst section and saving them separately in a new ipl file with same name in different folder.The original IPL file is updated to remove LOD models entries, which is very handy 
                          for creating Binary IPLs


I may implement alot of new features and tools in it in future but that is it for now , lemme know if it was helful for you ;) 
