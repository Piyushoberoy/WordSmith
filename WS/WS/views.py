import json
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    user_email, user_name = "", ""
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
        user_email = request.user.email
        
    return render(request, 'home.html', {
            'user_name': user_name,
            'user_email': user_email
        })
def getMessage(name, email, message):
    return f"""
<html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f7fc;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                color: #2C3E50;
                text-align: center;
            }}
            .highlight {{
                color: #1ABC9C;
                font-weight: bold;
            }}
            .details {{
                margin-top: 20px;
                font-size: 16px;
                line-height: 1.6;
            }}
            .details p {{
                margin-bottom: 10px;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 14px;
                color: #777;
            }}
            .footer a {{
                color: #1ABC9C;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Feedback Submission</h2>
            <div class="details">
                <p><span class="highlight">Name:</span> {name}</p>
                <p><span class="highlight">Email:</span> {email}</p>
                <hr>
                <p><span class="highlight">Message:</span></p>
                <p>{message}</p>
            </div>
            <div class="footer">
                <p>Thank you for your feedback! Feel free to <a href="mailto:{email}">contact us</a> anytime.</p>
            </div>
        </div>
    </body>
</html>
"""


@login_required
def send_feedback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        subject = f"New Feedback from {name}"
        body = getMessage(name, email, message)
        # body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        recipient = "ynr24piyush@gmail.com"

        try:
            email = EmailMessage(
                subject,
                body,
                email,  # From email
                [recipient],  # Recipient(s)
            )
            email.content_subtype = "html"  # Set content type to HTML
            email.send()
        except Exception as e:
            print("Error sending email:", e)
            return JsonResponse({"success": False})

    return JsonResponse({"success": False})
