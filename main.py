import webapp2
from handlers import *

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/API/comment', CommentResource),
        webapp2.Route(r'/API/archive', ArchiveResource),
        webapp2.Route(r'/API/article', ArticleResource),
        webapp2.Route(r'/API/articlelist', ArticleListResource),
        webapp2.Route(r'/API/articlekeyfromslug', ArticleKeyFromSlugResource),
        webapp2.Route(r'/blog/<slug:.*>/', ArticleFromSlug), #hack
        webapp2.Route(r'/blog/<slug:.*>', ArticleFromSlug),
        webapp2.Route(r'/blog', OldRedirect),
        webapp2.Route(r'/feeds/latest/',ArticleLastRSS),
        webapp2.Route(r'/article/<key:.*>', ArticlePage),
        webapp2.Route(r'/manage/edit/<key:.*>', EditPage),
        webapp2.Route(r'/manage/delete/<key:.*>', DeletePage),       
        webapp2.Route(r'/manage', ManagePage),
        webapp2.Route(r'/archive', ArchivePage),
        webapp2.Route(r'/', MainPage)
    ], debug=True)
