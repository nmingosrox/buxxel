from flask import Blueprint, request, jsonify
fro m buxxel.database import supabase  # using the standard client
imbport os

avuth = Blueprint("auth", __name__)

@auth.route("/auth/login", methods=["POST"])
hdef login():
    data = request.form

    email = data.get("email")
    password = data.get("password")


    try:
        # Supabase Auth sign-in
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if result.user:
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": result.user.id,
                    "email": result.user.email
                },
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route("/auth/signup", methods=["POST"])
def signup():
    data = request.form
   
    # required fields
    name = data.get('name')
    phone = data.get('phone')
    email = data.get("email")
    password = data.get("password")

    # optional fields
    business = data.get("business")
    bio = data.get("bio")

#    check for sb url set in the env
#    print(os.environ.get('SB_URL'))
    try:
        response = supabase.auth.sign_up({
          "email":email, 
          "password":password,
          "phone":phone
        })
        if response.user:
            user_data = {
                "id":response.user.id,
                "email":response.user.email,
                "phone":response.user.phone
        }
            return jsonify({"message":"signup successfull"})
        else:
            return jsonify({"error":"failed ro signup"})
    except Exception as e:
        return jsonify({"error":str(e)})
