# ECommerce REST API
This RESTful API designed for an ecommerce activity is developed with Django.
The User class has been extended to account for useful shipping information.
The Models allow to manage Products, Categories, Discounts, Cart, Orders.
Admin endpoints allow to CRUD all stored data and to ban/unban users.

It employs [Gunicorn](https://github.com/benoitc/gunicorn) for deployment.
It uses a Postgres instance on Railway if deployed there, if it detects being on a local development machine it uses a local sqlite db.

## Implementation choices
The user ban check is in place in the UserLoginSerializer instead of in the function-based view.

The cart and order system are somewhat elaborate and work with the Product stock levels. The order status transitions are carefully managed
to avoid nonsense order logic. 
The discounts have an expiry date and apply to a specific Category of Products, so that when applied on the cart they don't
discount the entire cart products but only the ones that share the discount Category.

The API manages three levels of permission:
- Normal user: can view products, categories, add items to cart, checkout, and update its profile.
- Moderator: Normal user permissions in addition to the ability of banning/unbanning users, retrieving the list of users. Moderators cannot ban Admins. **Managed with custom permission IsModerator**.
- Admin: Has access to the API order manager, discount manager, and of course user manager like the Moderator. It's the only level that can create new products and categories.

## Security
Because only simple Token Authentication is used, no cookies are involved and thus **CSRF is unnecessary**. This application had all the unnecessary Django apps and middleware removed. 

The Database is a **PostgreSQL instance** deployed on Railway. The credentials are loaded from the environment.

The Django SECRET_KEY is generated automatically at the start of the application and **stored on disk**. It never appears in the source code, changes
every time the application starts and is not served on any path of the domain.

The application is **dockerized** in a barebone debian+python environment and listening on port 8000. The container is then exposed to port 443 on the URL https://ecommerce-django-production-f55b.up.railway.app.


# Testing information
The **sandokan** user (login email:pwd = sandokan@gmail.com:sandokan@gmail.com) is an Admin/is_staff user (has IsAdmin permission).
The **yanez** user (yanez@gmail.com:yanez@gmail.com) is a Moderator user.
## HTML/JS Client
A sample client can be accessed from this [Github Page](https://loremol.github.io/ecommerce-client/). This is its [corresponding repository](https://github.com/loremol/ecommerce-client).
## Troubleshooting
Cloning the repo back to my machine I encountered an error with carriages. If the docker ENTRYPOINT doesn't seem
to be found try setting this on git: `git config --global core.autocrlf input`. After, clone again the repo and try again.

# Endpoints
The following list provides an overview of the available endpoints:
### Accounts
*   **Authentication Endpoints**
    *   `POST /auth/register/`: Register a new user
    *   `POST /auth/login/`: Login an existing user
    *   `POST /auth/logout/`: Logout the current user
    *   `GET /auth/profile/`: Get the current user's profile information
    *   `PUT /auth/update/`: Update the current user's profile information
    *   `PUT /auth/ban/`: Ban a user
    *   `PUT /auth/unban/`: Unban a user
*   **Admin Endpoints**
    *   `GET /auth/users/`: List all users
    *   `GET /auth/users/<int:pk>/`: Get a specific user's information

### Products
*   **Category Endpoints**
    * `GET /store/categories/`: List all categories
    * `POST /store/categories/create/`: Create a new category
    * `PUT /store/categories/update/<int:pk>/`: Update an existing category
    * `DELETE /store/categories/delete/<int:pk>/`: Delete a category
*   **Product Endpoints**
    * `GET /store/products/`: List all products
    * `POST /store/products/create/`: Create a new product
    * `PUT /store/products/update/<int:pk>/`: Update an existing product
    * `DELETE /store/products/delete/<int:pk>/`: Delete a product

### Cart
*   **Cart Endpoints**
    *   `GET /cart/`: Get the cart details
    *   `POST /cart/add/`: Add an item to the cart
    *   `POST /cart/clear/`: Clear the cart
*   **Discount Endpoints**
    *   `POST /cart/apply_discount/`: Apply a discount
    *   `GET /cart/discounts/`: Get all available discounts
    *   `POST /cart/create_discount/`: Create a new discount
    *   `DELETE /cart/delete_discount/<int:pk>/`: Delete a discount

### Orders
*   **Order  Endpoints**
    *   `GET /orders/`: Get own orders
    *   `GET /orders/<int:pk>/`: Get the details of a specific order
*   **Checkout and Update Endpoints**
    *   `POST /orders/checkout/`: Initiate checkout for a Cart instance
    *   `POST /orders/update/<int:pk>/`: Update an existing order
*   **Admin Endpoints**
    *   `GET /orders/all/`: Get all the orders from all the users
    *   `DELETE /orders/delete/<int:pk>/`: Delete a specific order
    *   `GET /orders/stats/`: Get statistics about orders