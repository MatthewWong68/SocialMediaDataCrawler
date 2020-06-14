class Post:
  
  id = ""
  full_text = ""
  author_name = "" 
  crawled_dt = ""
  post_dt = ""
  like = 0
  comment = 0

  def __init__(self, id, full_text, author_name, crawled_dt, post_dt, like, comment):
    self.id = id
    self.full_text = full_text
    self.author_name = author_name
    self.crawled_dt = crawled_dt
    self.post_dt = post_dt
    self.like = like 
    self.comment = comment

  def toString(self):
      print("ID of the post: " + self.id + ". The whole text of the post: " + self.full_text + ". The author of the post:" +
      self.author_name + ". Crawled time:" + self.crawled_dt + ". Post time: " + self.post_dt + ". Like: " + self.like +
      ". Comment" + self.comment + ".")
      print(" ")