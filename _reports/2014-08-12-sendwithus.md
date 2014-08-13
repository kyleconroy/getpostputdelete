A 403 with no body is returned when no key is present. You should always return
a body, especially for errors.

Your API responds to traffic over HTTP, which means API tokens can be trivially
stolen by anyone sniffing traffic. I'd suggest shutting down access to port 80.
Also add the [Strict-Transport-Security][0] header to your API. It should take 10
minutes to add, and makes non-SSL HTTP connections less frequent.

[0]: https://www.owasp.org/index.php/HTTP_Strict_Transport_Security

## Authentication

Basic authentication is a good start, but support for OAuth2 would be great.
This will make it easier to build mobile applications without distributing a
private key inside the app.

Since you are showing me my key, I assume you're storing them as plaintext. It
would be better to generate the key once and give it to the user, and store
only the hashed version (just like passwords). See GitHub personal access
tokens for an implementation.

Content-Type: application/json

## Versioning

Since you're planning a new version of the API, I'd suggest reworking your URL
structure. Ditch `/api/v1` completely, and opt to use headers for versioning
instead of hard-coded versions in the URL.

Follow Heroku's lead and version your API using the Accept header[2]. GitHub
did this with version 3 of their API, and Stripe versions using the
`Stripe-Version` header.

Once you have more than one version, create an API changelog[1] so clients know
what's changed.

[1]: https://stripe.com/docs/upgrades
[2]: https://github.com/interagent/http-api-design#version-with-accepts-header

## Content-Type

Your `Content-type` headers are missing the character set. All your responses
should be rendered in UTF-8.

    Content-Type: application/json; charset=utf-8

## General API

### URLs

Provide resource URLs in the resource body

```js
[
  {
    "created": 1407909156,
    "id": "tem_g3L7Cw6Hp5wUaf395LehwK",
    "url": "https://api.sendwithus.com/templates/tem_g3L7Cw6Hp5wUaf395LehwK",
    "name": "Invoice Email",
    ...
  },
]
```

### Pagination

Once you're at a larger size, you'll find that offset-based paging no longer
scales. I'd suggest to head this off by providing a `Link` header in
responses[3]. Clients can just parse this instead of constructing their own
URLs, allowing you to change pagination styles for free!

```
Link: <https://api.sendwithus.com/api/v1/templates?offset=100>; rel="next"
```

[3]: https://developer.github.com/guides/traversing-with-pagination/

### Time

Make sure that you're generating timestamps from UTC dates, not dates in
Pacific time.

### Response Format

Having `status` and `success` attributes in your responses is redundant, as
that information is encoded in the HTTP status code.

## Resources

### Templates

> GET /templates

There is no documentation on how to paginate through templates. I'm assuming
that I can use the `count` and `offset` parameters. 

> POST /templates

When providing invalid JSON to the `/templates` endpoint, I get a very
unfriendly error message in response.

```
No JSON object could be decoded
```

Instead, return a JSON object describing the error and how to fix it.

```js
{
  "code":  "invalid_body",
  "error": "No JSON object could be decoded",
  "url":   "https://www.sendwithus.com/docs/api/errors#invalid_body"
}
```

The same goes for missing parameters. This error message can't be parsed by a
client Also, this error doesn't make any sense, as email isn't a required
parameter. Maybe this refers to `name`?

```
invalid email name
```

Be explicit in what parameter is wrong

```js
{
  "code":  "invalid_parameter",
  "param": "email",
  "error": "Invalid email address",
  "url":   "https://www.sendwithus.com/docs/api/errors#invalid_parameter"
}
```

### Sending Emails

The `/send` endpoint should probably be renamed to `/messages`, as `send` is
not a resource.

### Logs

When multiple parameters have the same prefix, you should be using nested
objects instead.

```js
[
  {
    "object": "log",
    "id": "log_asdf1234qwerty",
    "created": 1234567890,
    "recipient": {
      "name": "Brad",
      "address": "brad@email.com"
    },
    "status": "opened",
    "message": "SendGrid: Message has been opened",
    "email": {
      "id": "as8dfjha8dap",
      "name": "Order Confirmation",
      "version": "Version A"
    },
    "events_url": "/api/v1/logs/log_asdf1234qwerty/events"
  }
]
```

The concept of logs having events is strange. Maybe `logs` should live under
`messages`? Not sure

### Rendering Templates
### Customers
### Drip Campaigns
### Segments
### Multi-Language
### Batch API Requests

### /address

Instead of return a `geocode_errors` message, have all address results return
the same attributes, including a boolean `deliverable` field.

Floats, such as `lat` and `lng`, should be numbers, not strings.

```js
{
  "lat": 37.7711831,
  "lng": -122.4518261,
  "deliverable": true,
  "exact_match": true,
  "location_id": 2629,
  "address": ["1995 Oak Street, San Francisco CA"]
}
```

### GET /parcels

The `total_parcel_count` will eventually become a bottleneck in API responses.
I'd suggest removing the field entirely (Seriously, this has happened at both
Twilio and Stripe).

The `parcels_per_page` attribute should be renamed to `page_size` to provide a
consistent paging interface over all resources.

Consider using the [Link Header][3] to pre-computer paging URLs for clients.

[3]: https://developer.github.com/guides/traversing-with-pagination/

### POST /parcels

This endpoint is designed to support both `application/x-www-form-encoded` and
`application/json`, even though you say the API only supports JSON. This
endpoint becomes much cleaner if you stick with just JSON, as you can nest
similar parameters. Instead of 

```js
{
  "orig_min": "2014-08-11T21:01:39Z",
  "dest_max": "2014-08-11T21:01:39Z",
  "orig_address": "",
  "dest_address": "",
  "orig_instructions": "",
  "dest_instructions": "",
  "description": "",
  "orig_name": "",
  "dest_name": "",
  "orig_phone": "",
  "dest_phone": ""
}
```

you can do

```js
{
  "origin": {
    "delivery": "2014-08-11T21:01:39Z",
    "address": "",
    "instructions": "",
    "name": "",
    "phone": ""
  },
  "destination": {
    "delivery": "2014-08-11T21:01:39Z",
    "address": "",
    "instructions": "",
    "name": "",
    "phone": ""
  }
  "description": ""
}
```

Better yeah?

Phone numbers should only be accepted in E.164. For example, all US numbers
should be prefixed with +1. Use [libphonenumber][phone] to parse the numbers.

[phone]: https://code.google.com/p/libphonenumber/

### GET /parcels/:uuid

Nice job using UUIDs. For clients, I'd suggest also proving a `url` attribute.

```js
{
    "uuid": "99f95577dd3a4d7298de5b3b6dca6c09", 
    "url": "https://gorickshaw.com/parcels/99f95577dd3a4d7298de5b3b6dca6c09", 
    ...
}
```

Phone numbers should also be formated as E.164.

### DELETE /parcels/:uuid

I tried deleting the same parcel twice and caused a server error. Oops.

### PUT /parcels/:uuid

PUT doesn't mean what you think it means. Only support PATCH.

### GET /parcels/:uuid/notifications

This resource is inconsistent with the `/parcels` resource. Either return an
array in both, or return an object in both. Don't mix and match.

### GET /parcels/:uuid/notifications/:uuid

No need to nest notifications under parcels. You should have a top-level
`/notifications` resource that lists all notifications for your account. To get
a notification, you'd use the `/notifications/:uuid` endpoint.

You can keep the `/parcels/:uuid/notifications` resource.

The phone numbers here aren't formatted the same as the parcels resource.
Again, this should be E.164.
