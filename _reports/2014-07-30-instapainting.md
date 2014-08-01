Chris,

Congratulations, you're my first report. Take anything I say with a grain of
salt, and feel free to disagree with anything I say

## Red Flags

> Step 3 can be achieved by directly placing the order through the API
> using a credit card on file,

It doesn't look like you support this feature yet. Don't implement it, as
you'll need to ensure your entire setup is PCI compliant, a process you don't
want to go through. Stick to only supporting payment through the `payment_uri`.

## Authentication

Use a separate subdomain for your API. I'd suggest `api.instapainting.com`. The
reason is my next suggestion.

Since you're using Basic auth, you don't want to accept connections over HTTP,
as you'll leak credentials. Currently, the API redirects non-SSL traffic to the
SSL endpoint. Instead, change to a sub-domain which doesn't expose port 80.

The public / private placement is cute, but causes confusion. What happens if I
include a public AND a private key? Pick one location for the key to live. I'd
suggest the password portion.

## Versioning

Don't put versioning information in the URL. Stripe did this and we all wish we
could take it out. Instead, put the version information in a header. My
suggestion is the `Accept` header.

    Accept: application/json; version=1

Peg clients that don't provide a version header to the first version of the
API, not the latest version.

With versioning outside the URL, you'll be free to make breaking changes more
often. For example, Stripe has released 4 new versions in the last two
months, all containing small but important changes. None of these changes would
have justified changing the URL.

## Errors

All error responses (status code >= 400) should return an error object. This
error object should be the same throughout the API. I like Heroku's suggestion:

```
{
  "id":      "rate_limit",
  "message": "Account reached its API rate limit.",
  "url":     "https://docs.service.com/rate-limits"
}
```

## URL Design

Here is what I think the URLs should look like. All I did was make things
plural

    https://api.instapainting.com/orders
    https://api.instapainting.com/orders/:id
    https://api.instapainting.com/orders/:id/items
    https://api.instapainting.com/orders/:id/items/:id
    https://api.instapainting.com/shipments
    https://api.instapainting.com/shipments/:id

The last two endpoints are new, see the orders section for explanation.

## Resources

It's helpful to add a prefix to all resource IDs, so that users can easily tell
IDs apart. For example, to differentiate between items `it_a5de35ad` and orders
`or_ad7a98d7`

I'd also suggest adding a `url` parameter to all resources, making them easier
to fetch for clients.
 
### GET https://api.instapainting.com/orders

Instead of making your customers building paging URLs, provide a Link header
they can parse and use.

```
Link: <https://api.instapainting.com/orders?page=1>; rel="next"
```

For more information, see the GitHub API documentation on paging

https://developer.github.com/guides/traversing-with-pagination/

### POST https://api.instapainting.com/orders

The `phonenumber` should be in E164 format, which just requires a + in front of
the number.

The `campaign` parameter should have a documented max-length.

Rename the `user_identifier` field to `user`.

Pick one: `notes` or `instructions` as they are both notes for the artist.

### GET https://api.instapainting.com/orders/:id

The order schema is a bit crowded. I'd move all shipping information into a
nesting shipping object, give it a unique id, and expose it under `/shipments`.
Also, you may want to use a `status` field instead of ready and error booleans.

```
[{
  "id": "or_53d33e6d1d41c8543bc2d1f2",
  "url": "https://api.instapainting.com/orders/or_53d33e6d1d41c8543bc2d1f2",
  "shipment": {
    "id": "sh_41c8543bc2d1f2",
    "status": "pending",
    "tracking_number" : null,
    "dimensions" : null,
    "address": null
  }
}]
```

The `timestamp` field is too generic. Use `created` so that users know what it
means. It leaves you room to add an `updated` parameter later.

### POST https://api.instapainting.com/orders/:id/items

If you want to support both JSON and form-encoded, you'll need to change how
you handle `coords`. I'd suggest using "named" form parameters instead of a
comma-separated list. Also use x1 and y1 for consistency.

    -d coords[x1]=3 -d coords[y1]=3 -d coords[x2]=3 -d coords[y2]=3

Give the options object parameter the same treatment

    -d options[stretching]=stretched -d options[style]=photorealistic

You're limiting yourself only supporting file uploads. I'd suggest allowing
URLs as well.

The `pricing` key doesn't make much sense. Just move all the nested keys to the
top level

Create a unique id for items as well, don't use a filename.

Renamed `uri` to `photo_url`.

Return a full item object instead of a pricing object

```
{
  "photo_url": "https://instp.imgix.net/53d33e6d1d41c8543bc2d1f2_MyPic.jpg",
  "url": "https://api.instapainting.com/orders/or_53d33e6d1d41c8543bc2d1f2",
  "id": "it_124213sd1231",
  "fees" : {
    "stretched": "stretching"
  },
  "dimensions" : {
    "height" : 22,
    "width" : 22
  },
  "price" : 12503,
  "minSize" : [
    150,
    150
  ],
  "aspectRatio" : 1,
  "shipping" : 1200
  "quantity" : 1,
  "options" : {
     "stretched": {
       "stretched": 1000,
       "rolled": 0
     }
  },
  "preview" : null,
  "qc_status" : null,
  "coords" : {
    "x1" : 0,
    "y1" : 0,
    "y2" : 300,
    "x2" : 300
  },
  "price" : null,
  "redo_count" : 0,
  "fix_count" : 0,
  "instructions_read" : null,
  "instructions" : null
}
```
