Paul,

Here's my report / review. Take anything I say with a grain of
salt, and feel free to disagree!


## Website

My review will mainly be about the APIs you expose for your users, but I had
one piece of feedback on the site. For a given API, say [Reverse Image
Search][search], it's very difficult to find the source code and API link. 

I'd suggest rendering the API snippet below the included form so it's easier to
find. You'll also have more room for code samples. 

[search]: https://api.blockspring.com/users/pkpp1233/blocks/5a1b66ef208007c51a45fda220dbe8db

## Authentication

Nice to see that you're using a separate subdomain for your API.

You're currently using url-based authentication. However, it's better to use
authentication through a header, as it will never be cached. Firefox has
started caching some SSL urls, so it's better to try and remove sensitive from
the URL. I'd suggest using basic authentication.

Your API is accessible over HTTP, which means API tokens can be trivially
stolen by anyone sniffing traffic. I'd suggest shutting down port 80 for
`sender.blockspring.com`, so that non-SSL requests do not work.

## Versioning

You're in a fantastic place to provide APIs that never break. Since each API on
Blockspring is a single file, you should be storing versions of that file in
git, or some kind of scm system.

When a user makes requests to an API, let them specify a revision of commit
hash as a version, like so.

    Accept: application/json; version=d709334

That allows you to pull the specific version of the file, meaning a client will
never get a different version, making your service much more reliable.

Right now, I can't depend on an API, because someone could make a breaking
change without my knowledge.

## Content-Type

Again, you're in a strange position as you let anyone create an API. The
Content-Type headers do not match the return output. For example, the [Reverse
Image Search][search] returns it's results as JSON, but you serve a
Content-Type of `text/html`.

Either allow authors to pick a content type, respect the accept header passed
in by the client, or parse the return value to try and infer a content type.

Also, you mention in the docs that Blockspring will zip up files and return
them as a single blob. While this may be helpful for data programs and
visualizations, it's a strange way to interact with an API.

## Errors

I created an API that threw an exception. Even though my script errored, a 200
was still returned by the API. I'd suggest standardizing on error formats for
failing programs.

This error object should be the same throughout the API. I like Heroku's
suggestion:

```
{
  "id":      "rate_limit",
  "message": "Account reached its API rate limit.",
  "url":     "https://docs.service.com/rate-limits"
}
```

## Final Thoughts

Overall, blockspring is a good start, but you need to give more tools to API
creators to make more robust and standard APIs. The lack of any error
information is the first issues I would tackle.

