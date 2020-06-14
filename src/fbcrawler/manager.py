class Manager:
  
  place = ""
  number = 0

  def __init__(self, place, number):
    self.place = place
    self.number = number

  def toString(self):
      print("Place: " + self.place + ". Number: " + self.number + ".")
      print(" ")