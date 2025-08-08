# Coding challenge for Avoxi
Coding challenge for Avoxi

## Scenario:
Our customers are requesting we restrict users logging in to their UI accounts from selected countries so that they can prevent them from outsourcing their work to others.  For an initial phase one we’re not going to worry about VPN connectivity, only the presented IP address.

The team has designed a solution where the customer database will hold the white listed countries and the API gateway will capture the requesting IP address, check the target customer for restrictions, and send the data elements to a new service you are going to create.  

The new service will be an HTTP-based API that receives an IP address and a list of allowed countries.  The API should return an indicator if the IP address is within the allowed countries or not.  You can get a data set of IP address to country mappings from https://dev.maxmind.com/geoip/geoip2/geolite2/.

## Evaluation Criteria:
We do our backend development in Go (Golang) and prefer solutions in that language but can accept solutions in any major programming language.

You are allowed to utilize AI coding tools to complete this coding challenge but are expected to provide usage details in submission notes.

We'll be explicitly looking at coding style, code organization, API design, and operational/maintenance aspects such as logging and error handling.  We'll also be giving bonus points for things like
* Documenting a plan for keeping the mapping data up to date.  Extra bonus points for implementing the solution.
* Including a Docker file for the running service
* Including a Kubernetes YAML file for running the service in an existing cluster
* Exposing the service as gRPC in addition to HTTP
* Other extensions to the service you think would be worthwhile.  If you do so, please include a brief description of the feature and justification for its inclusion.  Think of this as what you would have said during the design meeting to convince your team the effort was necessary.

## My Solution:
I chose to implement the python Web Service Client. By using the geoip2 web service, we ensure that the data is always up to date.
Swagger Link: http://127.0.0.1:8000/swagger/

**Note** the python package is supported as an official Client API from MaxMind.
There is an equivalent third-party API for Go, but it is not officially supported by MaxMind - https://pkg.go.dev/github.com/savaki/geoip2#section-readme.
If we didn't want to go the route of an unsupported API, we could set up a chron job to manually download the latest binary database on a nightly basis and query that.

### AI Usage:
I used Claude Code to generate the test cases, and then tweaked them to ensure the assertions were helpful and the tests run

### Extensions:
Use the Database exposed by GeoIP to get the data when we receive and `OutOfQueriesError` from the API.
* Since I'm basing my code on the free GeoLite, there are only 30 hits allowed daily
* Customers should still get data if you go above this number
* Set up a nightly job to pull the latest binary database
* In case of `OutOfQueriesError`, query the database for the iso code
* **Note** This could also be used if we decide that we don't want to introduce the potential latency of querying another service 

### Disclosures: 
I didn't start the timer for the 4 hours until after I had done the initial configuration of the project
* Creating repo
* Creating Django project
* Creating MaxMind account