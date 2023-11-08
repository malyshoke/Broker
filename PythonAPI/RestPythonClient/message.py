MT_INIT		= 0
MT_EXIT		= 1
MT_GETDATA	= 2
MT_DATA		= 3
MT_NODATA	= 4
MT_CONFIRM	= 5
MT_GETLAST  = 6
MR_BROKER	= 10
MR_ALL		= 50
MR_USER		= 100

class Message:

    def __init__(self, To, From, Type, Data = None):
        self.To = To
        self.From = From
        self.Type = Type
        self.Data = Data