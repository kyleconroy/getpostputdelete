Ivan,

I really need to write a blog post to share with people. In the mean time, here are some tips:

- Don't return a total count on list resources, as this doesn't scale.
- Versioning information should be in a header, preferably the Accept header.
- An API request without a version should either be an error, or use the lowest
  API version. Defaulting to the latest version is a recipe for broken applications.
- Clients shouldn't have to construct paging URLs, so return the Link header
  [1].

Also check out Heroku's API design docs[0]. Ignore the section on using the
Accept-Range header for paging. 

[0]: https://github.com/interagent/http-api-design
[1]: https://developer.github.com/guides/traversing-with-pagination/

This turned out to a bit more popular than I thought, so it's going to take
some time to fulfill all the requests I received. Once I finish looking through
your API, I'll send an email with my comments. Talk to you soon!

Kyle
