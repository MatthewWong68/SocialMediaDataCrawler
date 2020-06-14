class Feed:
  
  id = ""
  full_text = ""
  author_name = "" 
  reactions = ""
  crawled_dt = ""
  post_dt = ""
  like = 0
  love = 0
  angry = 0
  wow = 0
  haha = 0
  sad = 0
  comment = 0
  share_count = 0

  def __init__(self, id, full_text, author_name, reactions, crawled_dt, post_dt, like, love, angry, wow, haha, sad, comment, share_count):
    self.id = id
    self.full_text = full_text
    self.author_name = author_name
    self.reactions = reactions
    self.crawled_dt = crawled_dt
    self.post_dt = post_dt
    self.like = like 
    self.love = love
    self.angry = angry
    self.wow = wow
    self.haha = haha
    self.sad = sad
    self.comment = comment
    self.share_count = share_count

  def toString(self):
      print("ID of the post: " + self.id + ". The whole text of the post: " + self.full_text + ". The author of the post:" +
      self.author_name + ". Number of reactions: " + self.reactions + ". Crawled time:" + self.crawled_dt + ". Post time: " + 
      self.post_dt + ". Like: " + self.like + ". Love: " + self.love + ". Angry: " + self.angry + ". Wow: " + self.wow + 
      ". Wow: " + self.wow + ". Sad: " + self.sad + ". Comment" + self.comment + ". Share: " + self.share_count + ".")
      print(" ")