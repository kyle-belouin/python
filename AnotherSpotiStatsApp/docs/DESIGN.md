<h2>Layout of components:</h2>

<h3>Top level, public facing index page:</h3>

* We will need a page to display to any visitor to the site who is not logged in. This page should give a summary of the app's capabilities, and give a very clear path toward users logging into our website or signing up.


<h3>User authentication and management:</h3>

* We will need a login page, in which registered users are able to access the content of the website.

* The login page must facilitate new users who wish to sign up to the website.
  * Should have a message on this page advising people to NOT utilize the same login as their Spotify account.
  
* The login page also facilitate existing users who may have forgot their password.

* The login page must be able to send new users activation emails. The page must also be able to email password reset instructions to existing users, if requested.

* We will need different levels of access, at least a Users role and an Administrators role.
  * Users should be able to update their own basic information, such as e-mail address.
  * Administrators will have access to a special admin page, with the ability to create or remove users, and perform other user administrative tasks. Admins will have the ability to update user's basic information.
  * Any user accessing our website must be a registered user. We can have an informational top-level page, but nobody shall be able to perform any action other than reading this top page if they are not logged in.
  * Any site visitor must be able to register with our website from the login page.
 

<h3>Main application/user experience:</h3>

* Web design shall be responsive and work with Mobile clients. Design for Mobile first!

* Upon login to the app, if the user is not authenticated with a Spotify account yet, they should be first met with the login to Spotify's platform.

* Once users are authenticated to both our website and the Spotify platform, our application should appear and be usable to them.
  * Users will be able to choose from available data, from a dropdown or otherwise, for the web app to go out and collect data from Spotify, then display it immediately to the user in a readable form.
  * Users who connect to a Spotify account shall have a way to logout of their connected account at any time.
  * Errors can happen, so we must remember to include some error handling, or otherwise human readable output that users can understand if something went wrong.

* This output must be at least exportable as a CSV file.
  * Would desire this to be an Excel spreadsheet file (XSLX).
  * Would most desire the capability to email oneself this report.
 

<h3>Security/Implications:</h3>

* For us as the developers, we will need to utilize our own Spotify accounts to test our website out and develop incrementally. There will be no pressure if a developer doesn't want to use their own account.

* For any classes or methods/functions we create in Python, we must have tests for them. 100% coverage or bust.

* What we are asking users to do on our website must be taken seriously, and we must hold ourselves accountable to the integrity of their data. This means:
  * We should write a basic privacy statement that is visible to anyone who accesses the site, logged in or not.
  * Any piece of sensitive data, such as a user's password into the web site, shall NEVER be stored as plain-text in our database, nor should plain-text credentials EVER be passed over the network on its path to and from our website. If a user submits credentials into the website, we must immediately encrypt it. All passwords must be some form of hash that nobody can understand and we must store this data in a secure way.
  * (If we can do it) the functions to email users reports must be robust and ensure that users are only able to email themselves. For example, we can't have advanced users hijack related API calls to use our website to send email to anybody.

* If possible, we must set the website up to run only on HTTPS. We might be able to set up self-signed certificates to accomplish this, this will require research. It would be terrible to run this kind of website over just HTTP.

* User Spotify login data shall not be stored on our website or in our database. The only thing we should need to retain is the user's authentication token and most likely their User ID or email for Spotify.

* The website must do what we say it does, and nothing more.

* (If we have time to research it) The website should be immune to SQL injection attacks.
