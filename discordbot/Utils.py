def getCommand(command):
	command = command[1:]
	returnValue = ['',[]]
	for i in range(len(command)):
		if command[i] == " ":
			for j in range(i, len(command)):
				if command[j] != " ":
					returnValue[0] = command[:i].lower()
					command = command[j:]
					break;
			break;
		elif i == len(command)-1:
			returnValue[0] = command.lower()
			return returnValue
	buf = ""
	x = False
	for i in range(len(command)):
		if(command[i]==" "):
			x = True
		elif x and command[i] != " ":
			returnValue[1].append(buf)
			buf = command[i]
			x = False
		else:
			buf += command[i]
	if(len(buf)!=0):
		returnValue[1].append(buf)
	return returnValue

def getChannelLanguage(db, channelID):
    a = db.SELECT("ChannelsAndLanguages",["language"], "channelID = " + str(channelID))
    if len(a) == 0:
        db.INSERT("ChannelsAndLanguages", [["language", "en-EN"], ["channelID", str(channelID)]])
        return "en-EN"
    return a[0][0]