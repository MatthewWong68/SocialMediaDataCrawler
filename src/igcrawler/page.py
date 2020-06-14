class Page:
  
  author_name = ""
  posts = 0
  followers = 0
  following = 0

  def __init__(self, author_name, posts, followers, following):
    self.author_name = author_name
    self.posts = posts
    self.followers = followers
    self.following = following

  def toString(self):
    print("Author: " + self.author_name + ". Number of post: " + + self.posts + ". Number" + 
    " of followers: " + self.followers + ". Number of following: " + self.following)
    print(" ")