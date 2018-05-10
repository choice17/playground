echo enter command number
echo 1: bunny dump to out.mp4
echo 2: bunny dump to outpipe
echo 3: ourcam dump to outpipe
echo 

read -p "command number: "  number

if [ $number -eq 1 ] 
then
    rm out.mp4
    ffmpeg -i rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov -acodec copy -vcodec copy -f rawvideo out.mp4
fi

if [ $number -eq 2 ] 
then
    rm outpipe
    mkfifo outpipe
    ffmpeg -i rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov -acodec copy -vcodec copy -f rawvideo pipe:1 > outpipe
fi

if [ $number -eq 3 ] 
then
    rm outpipe
    mkfifo outpipe
    ffmpeg -i rtsp://admin:multitek123@192.168.10.107:554/Streaming/Channels/101 -acodec copy -vcodec copy -f rawvideo pipe:1 > outpipe
fi
