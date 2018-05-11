## ffmpeg useful command

## content table
- [ffplay](#ffplay)<br>
- [ffmpeg](#ffmpeg)<br>
- [ffprobe](#ffprobe)<br>

## ffplay
`ffplay -i {inputfile}`

## ffmpeg

`ffmpeg -i {inputfile} {outputfile}`

to dump the streaming (audio/video)   
`-acodec copy -vcodec copy`

embed subtitle to the file / streaming  
`ffmpeg -i {input} -f srt -i {.srt} -map 0:0 -map 1:0 -map 1:0 -c:v copy -c:a copy -c:s mov_text {output}`

## ffprobe  

simply get file metadata  
`ffprobe -i {inputfile}`

simply get streaming meta data  
`ffprobe -show_streams -i {in}`

