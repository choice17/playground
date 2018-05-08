@echo off
echo =================================================================
echo =RTSP streaming service                                         =
echo =using ffmpeg                                                   =
echo =for ffmpeg installation please visit https://www.ffmpeg.org/   =
echo =================================================================
echo.   
set /p 	  url="Enter url         : "
SET mypath=%~dp0
set /p output="Enter output file : "
set output=%mypath%%output%
echo.
echo Url entered		: %url%
echo Output file entered	: %output%
echo.
echo Press any button to continue dumping the streaming data ...
pause
start ffmpeg -i %url% -acodec copy -vcodec copy %output%

