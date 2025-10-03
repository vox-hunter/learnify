import resend
import random
import os

# Configure resend API key from environment variables
resend.api_key = os.environ.get("RESEND_API_KEY", "your-resend-api-key-here")

# Load HTML template
def load_verification_template():
    """Load the verification email HTML template"""
    template_path = os.path.join(os.path.dirname(__file__), "verification.html")
    try:
        # Try UTF-8 first
        with open(template_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        # If UTF-8 fails, try with UTF-8-sig (handles BOM) or latin-1
        try:
            with open(template_path, "r", encoding="utf-8-sig") as file:
                return file.read()
        except Exception:
            # Last resort: read as binary and decode, ignoring errors
            with open(template_path, "rb") as file:
                return file.read().decode("utf-8", errors="ignore")
    except FileNotFoundError:
        # Clean, spam-resistant fallback template with professional styling
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Loom Verification</title>
            <style>
                body, table, td, p, a, span, div { margin: 0; padding: 0; }
                body { font-family: Arial, Helvetica, sans-serif; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; background-color: #f3f4f6; }
                table { border-collapse: collapse; }
                .email-container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
                .header { background: linear-gradient(135deg, #6b46c1 0%, #9333ea 100%); padding: 40px 30px; text-align: center; }
                .header h1 { color: #ffffff; font-size: 32px; font-weight: bold; margin: 0; }
                .header p { color: #e0e7ff; font-size: 16px; margin: 10px 0 0 0; }
                .content { padding: 40px 30px; }
                .content h2 { color: #1f2937; font-size: 24px; text-align: center; margin: 0 0 20px 0; }
                .content p { color: #6b7280; font-size: 16px; line-height: 24px; margin: 0 0 20px 0; text-align: center; }
                .code-container { text-align: center; margin: 30px 0; }
                .code-box { 
                    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                    border: 2px solid #6b46c1;
                    border-radius: 12px;
                    padding: 25px;
                    display: inline-block;
                    margin: 0 auto;
                }
                .verification-code { 
                    font-size: 36px; 
                    font-weight: bold; 
                    color: #6b46c1; 
                    letter-spacing: 6px; 
                    font-family: 'Courier New', Courier, monospace;
                }
                .footer { background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb; }
                .footer p { color: #9ca3af; font-size: 14px; line-height: 20px; margin: 0; }
                .security-notice { 
                    background-color: #fef3c7; 
                    border-left: 4px solid #f59e0b; 
                    padding: 15px; 
                    margin: 20px 0; 
                    border-radius: 0 8px 8px 0;
                }
                .security-notice p { color: #92400e; font-size: 14px; text-align: left; margin: 0; }
                @media screen and (max-width: 600px) {
                    .email-container { width: 100% !important; }
                    .header { padding: 30px 20px !important; }
                    .header h1 { font-size: 28px !important; }
                    .content { padding: 30px 20px !important; }
                    .verification-code { font-size: 28px !important; letter-spacing: 4px !important; }
                    .code-box { padding: 20px !important; }
                }
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f3f4f6; padding: 20px 0;">
                <tr>
                    <td align="center">
                        <div class="email-container">
                            <!-- Header -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td class="header">
                                        <h1>🧠 AI Loom</h1>
                                        <p>Smart Learning Platform</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Content -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td class="content">
                                        <h2>Email Verification Required</h2>
                                        
                                        <p>Welcome to AI Loom! To complete your account setup, please verify your email address using the code below:</p>
                                        
                                        <div class="code-container">
                                            <div class="code-box">
                                                <div class="verification-code">{code}</div>
                                            </div>
                                        </div>
                                        
                                        <div class="security-notice">
                                            <p><strong>🔒 Security Notice:</strong> This verification code will expire in <strong>10 minutes</strong>. For your security, never share this code with anyone.</p>
                                        </div>
                                        
                                        <p>If you didn't create an account with AI Loom, please ignore this email and no action is required.</p>
                                        
                                        <p>Need help? Contact our support team or visit our help center.</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Footer -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td class="footer">
                                        <p>
                                            © 2025 AI Loom. All rights reserved.<br>
                                            This is an automated security email. Please do not reply.<br>
                                            <strong>AI Loom</strong> - Empowering Education with AI
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </div>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return random.randint(100000, 999999)

def send_verification_email(email: str, code: int, purpose: str = "registration"):
    """
    Send verification email with spam-resistant formatting
    
    Args:
        email: Recipient email address
        code: 6-digit verification code
        purpose: 'registration' or 'password_reset'
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        html_template = load_verification_template()
        html_content = html_template.replace("{code}", str(code))
        
        # Create clear, spam-filter-friendly subject lines
        if purpose == "password_reset":
            subject = "AI Loom - Password Reset Verification Code"
        else:
            subject = "AI Loom - Email Verification Code"
          # Prepare email parameters with best practices for deliverability
        params: resend.Emails.SendParams = {
            "from": "AI Loom Verification <verification@ailoom.me>",
            "to": [email],
            "subject": subject,
            "html": html_content,
            # Add text fallback for better deliverability
            "text": f"""
AI Loom - Email Verification

Your verification code is: {code}

This code will expire in 10 minutes for your security.

If you didn't request this verification, please ignore this email.

© 2025 AI Loom. All rights reserved.
This is an automated security email.
            """.strip()
        }

        email_response = resend.Emails.send(params)
        return True, f"Verification email sent successfully. ID: {email_response.get('id', 'unknown')}"        
    except (ValueError, KeyError, ConnectionError) as e:
        return False, f"Failed to send verification email: {str(e)}"
    except Exception as e:  # pylint: disable=broad-except
        return False, f"Unexpected error sending verification email: {str(e)}"

def verify_email_code(entered_code: str, stored_code: int):
    """
    Verify if the entered code matches the stored code
    
    Args:
        entered_code: Code entered by user (string)
        stored_code: Code stored in session/database (int)
    
    Returns:
        bool: True if codes match, False otherwise
    """
    try:
        return int(entered_code) == stored_code
    except (ValueError, TypeError):
        return False
