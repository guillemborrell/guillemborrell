angular.module('app', ['ngResource','ngSanitize']);

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


// Controller for the index page, that loads an entry list
function shareTwitter (article) {
    window.open(
	"https://twitter.com/share?url="+encodeURIComponent(
	    "http://www.guillemborrell.es/article/"+article.key
	)+"&text="+encodeURIComponent(
	    "Blog de Guillem Borrell: "+article.title),
	"Compartir con Twitter",
	"width=600,height=400"
    );
};

function shareFacebook (article){
    window.open(
	"https://www.facebook.com/sharer/sharer.php?u="+encodeURIComponent(
	    "http://www.guillemborrell.es/article/"+article.key),
	"Compartir con Facebook",
	"width=600,height=400"
    );
}

function shareTumblr (article){
    window.open("https://www.tumblr.com/share?v=3&u="+encodeURIComponent(
	"http://www.guillemborrell.es/article/"+article.key
    )+"&t="+encodeURIComponent(
	"Blog de Guillem Borrell: "+article.title),
		"Compartir con Tumblr",
		"width=600,height=400"
	       );
}

function shareGooglePlus (article) {
    window.open(
	"https://plus.google.com/share?url="+encodeURIComponent(
	    "http://www.guillemborrell.es/article/"+article.key
	)+"&text="+encodeURIComponent(
	    "Blog de Guillem Borrell: "+article.title),
	"Compartir con Twitter",
	"width=600,height=400"
    );
}

function fillArticle (article,sce) {
    return {
	"slug": article.slug,
	"when": article.when,
	"title": article.title,
	"text": sce.trustAsHtml(article.text),
	"keywords": article.keywords,
	"key": article.key,
	"comments": article.comments.reverse(),
	"ncomments": article.comments.length,
    }
}

function resetpage(){
    window.location.replace('/');
}


function MainPage($scope,$resource,$sce,$location){
    $scope.tag =  getParameterByName('tag')
    $scope.articles = [];
    $scope.shareTwitter = shareTwitter;
    $scope.shareFacebook = shareFacebook;
    $scope.shareTumblr = shareTumblr;
    $scope.shareGooglePlus = shareGooglePlus;
    $scope.articleListResource = $resource("/API/articlelist");
    $scope.taggedArticleListResource = $resource("/API/taggedarticlelist");

    if ($scope.tag){
	$scope.taggednext = '';
	var data = $scope.taggedArticleListResource.get(
	    {tag: $scope.tag}, function(){
		$scope.more = data.more;
		$scope.taggednext = data.next;
		$scope.taggedbutton = true;
		for (var i in data.articles){
		    $scope.articles.push(
			fillArticle(data.articles[i],$sce));
		}
	    }
	    
	);
    }
    else{
	var data = $scope.articleListResource.get( function(){
	    $scope.more = data.more;
	    $scope.next = data.next;
	    for (var i in data.articles){
		$scope.articles.push(
		    fillArticle(data.articles[i],$sce));
	    }
	}

						 );
    }
    
    $scope.loadnext = function(){
	var data = $scope.articleListResource.get(
	    {p:$scope.next}, function(){
		$scope.more = data.more;
		$scope.next = data.next;
		for (var i in data.articles){
		    $scope.articles.push(fillArticle(data.articles[i],$sce));
		}
	    }
	);
    }
    
    $scope.loadtag = function(thistag,reset){
	if (reset){
	    $scope.taggednext = '';
	}
	var data = $scope.taggedArticleListResource.get(
	    {tag:thistag, p:$scope.taggednext}, function() {
		$scope.tag = thistag;
		$scope.more = data.more;
		$scope.taggednext = data.next;
		$scope.taggedbutton = true;
		if (reset){
		    $scope.articles = [];
		    $("html, body").animate({ scrollTop: $("#body").offset().top }, "slow");
		}
		for (var i in data.articles){
		    $scope.articles.push(fillArticle(data.articles[i],$sce));
		}
	    }
	);
    }
}

// Controller for the article detail page
function ArticlePage($scope,$resource,$sce){
    $scope.key = location.pathname.split('/')[2];
    $scope.articles = [];
    $scope.shareTwitter = shareTwitter;
    $scope.shareFacebook = shareFacebook;
    $scope.shareTumblr = shareTumblr;
    $scope.shareGooglePlus = shareGooglePlus;
    $scope.replaceNewLines = function(text){
	return $sce.trustAsHtml(
	    text.replace(/\r\n/g, '<br />').replace(/[\r\n]/g, '<br />')
	);
    }

    var articleresource = $resource("/API/article?key=:q");
    var data = articleresource.get({q:$scope.key}, function(){
	$scope.articles.push(fillArticle(data,$sce));
    }
				  );
    $scope.newcomment = {"author": "",
			 "text": "",
			 "parent": "",
			 "check": "",
			 "when": null};
    
    $scope.submitcomment = function(){
	if ($scope.newcomment.check == "Borrell"){
	    var commentresource = $resource(
		"/API/comment",
		{},
		{ post: {method:'POST'}});
	    commentresource.post({
		"author": $scope.newcomment.author,
		"text": $scope.newcomment.text,
		"parent": $scope.articles[0].key,
		"safety": $scope.newcomment.check});
	    
	    $scope.articles[0].comments.push(
		{"author": $scope.newcomment.author,
		 "text": $scope.newcomment.text,
		 "parent": $scope.articles[0].key,
		 "when": null}
	    );
	    $scope.newcomment = {"author": "",
				 "text": "",
				 "parent": "",
				 "check": "",
				 "when": null};
	}
    }
}

function ManagePage($scope,$resource,$sce){
    $scope.newarticle = {"slug": "",
			 "title": "",
			 "text": "",
			 "keywords": "",
			 "secret" : ""}
    $scope.articles = [];

    var firstpageresource = $resource(
	"/API/articlelist:q");

    var data = firstpageresource.get({q:""}, function(){
	$scope.more = data.more;
	$scope.next = data.next;
	for (var i in data.articles){
	    $scope.articles.push(fillArticle(data.articles[i],$sce));
	}
    }
				    );


   $scope.loadnext = function(){
       var pageresource = $resource(
	   "/API/articlelist?p=:q");

       var data = pageresource.get({q:$scope.next}, function(){
	   $scope.more = data.more;
	   $scope.next = data.next;
	    for (var i in data.articles){
		$scope.articles.push(fillArticle(data.articles[i],$sce));
	    }
       }
				  );
   }


    $scope.submitarticle = function(){
	var articleresource = $resource(
	    "/API/article",{},{ post: {method:'POST'}}
	);
	articleresource.post({"slug": $scope.newarticle.slug,
			      "title": $scope.newarticle.title,
			      "text": $scope.newarticle.text,
			      "keywords": $scope.newarticle.keywords,
			      "secret": $scope.newarticle.secret
			     });
	$scope.newarticle.slug = "";
	$scope.newarticle.title = "";
	$scope.newarticle.text = "";
	$scope.newarticle.keywords = "";
	$scope.newarticle.secret = "";
	
    }
}

function EditPage($scope,$resource,$sce){
    $scope.key = location.pathname.split('/')[3];
    $scope.article = {"slug": "",
		      "title": "",
		      "text": "",
		      "keywords": "",
		      "secret" : "",
		      "key": "",
		      "when": ""}

    var articleresource = $resource("/API/article?key=:q");
    var data = articleresource.get({q:$scope.key}, function(){
	$scope.article.slug = data.slug,
	$scope.article.when = data.when,
	$scope.article.title = data.title,
	$scope.article.text = $sce.trustAsHtml(data.text),
	$scope.article.keywords = data.keywords,
	$scope.article.key = data.key
    }
				  );


    $scope.editArticle = function(){
	var articleresource = $resource(
	    "/API/article",{},{ post: {method:'POST'}}
	);
	articleresource.post({"slug": $scope.article.slug,
			      "title": $scope.article.title,
			      "text": $scope.article.text,
			      "keywords": $scope.article.keywords,
			      "key": $scope.article.key,
			      "when": $scope.article.when,
			      "secret": $scope.article.secret
			     });
	window.location.replace("/manage");
    }
}

function DeletePage($scope,$resource,$sce){
    $scope.key = location.pathname.split('/')[3];
    $scope.article = {"slug": "",
		      "title": "",
		      "text": "",
		      "keywords": "",
		      "secret" : "",
		      "key": "",
		      "when": ""}

    var articleresource = $resource("/API/article?key=:q");
    var data = articleresource.get({q:$scope.key}, function(){
	$scope.article.slug = data.slug,
	$scope.article.when = data.when,
	$scope.article.title = data.title,
	$scope.article.text = $sce.trustAsHtml(data.text),
	$scope.article.keywords = data.keywords,
	$scope.article.key = data.key
    }
				  );


    $scope.deleteArticle = function(){
	var articleresource = $resource(
	    "/API/article?key=:q&secret=:s",{q:$scope.article.key,
					     s:$scope.article.secret},
	    { del: {method:'DELETE'}}
	);
	articleresource.del();
	window.location.replace("/manage");
    }
}

function ArchivePage($scope,$resource){
    $scope.articles = [];
    $scope.archiveresource = $resource("/API/archive");

    var data = $scope.archiveresource.get(function(){
	$scope.more = data.more;
	$scope.next = data.next;
	$scope.articles = data.articles;
    }
				    );   
}

