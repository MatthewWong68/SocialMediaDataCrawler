class Page:
  
  author_name = ""
  ads = True
  page_created_date = ""
  total_number_of_manager = 0
  manager = ""

  def __init__(self, author_name, ads, page_created_date, total_number_of_manager, manager):
    self.author_name = author_name
    self.ads = ads
    self.page_created_date = page_created_date
    self.total_number_of_manager = total_number_of_manager
    self.manager = manager

  def toString(self):
      print("Author: " + self.author_name + ". Ads: " + self.ads + ". Page created date: " + self.page_created_date +
      ". Total number of manager: " + self.total_number_of_manager + ". Manager: " + self.manager)
      print(" ")