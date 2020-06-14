class Hashtag:

  feedID = ""
  text = ""

  def __init__(self, feedID, text):
    self.feedID = feedID
    self.text = text

  def toString(self):
    print("Hashtag: " + self.text + " appeared in post(PID): " + self.feedID)
    print(" ")