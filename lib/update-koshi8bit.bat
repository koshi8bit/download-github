::COPY TO lib\
@echo off

set source=G:\koshi8bit\prog\python\lib\lib\koshi8bit
set source2="%source%\"
set source="%source%"
set dest="%cd%\koshi8bit\"

echo source  %source%
echo source2 %source2%
echo dest    %dest%

IF %source2%==%dest% (
	echo SCRIPT DISABLED! Do not use in LIB folder
	pause
	exit
)


:RESTARTT
rd %dest% /Q /S
IF EXIST %dest% (
	echo ACHTUNG! Folder deletion failed!
    timeout /t 1
    GOTO RESTARTT
)
xcopy %source% %dest% /E /Y
attrib %dest%* /S +R
