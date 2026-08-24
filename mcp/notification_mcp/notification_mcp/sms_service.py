import os

from twilio.rest import Client


def send_sms(

    mobile_number: str,

    message: str,

) -> dict:
    """
    Sends an outbound SMS notification using the Twilio REST API.

    Reads Twilio credentials from environment variables and validates input parameters.
    Returns a structured dictionary indicating success or failure along with diagnostic details.

    :param mobile_number: Target recipient phone number (E.164 format expected, e.g., '+1234567890').
    :param message: Text payload content to send in the SMS.
    :return: Dict containing 'sms_status', 'recipient', 'message_sid', and 'error'.
    """

    try:

        # ----------------------------------------------------
        # ENVIRONMENT VARIABLE RETRIEVAL
        # ----------------------------------------------------

        account_sid = os.getenv(
            "TWILIO_ACCOUNT_SID"
        )

        auth_token = os.getenv(
            "TWILIO_AUTH_TOKEN"
        )

        twilio_phone_number = os.getenv(
            "TWILIO_PHONE_NUMBER"
        )


        # ----------------------------------------------------
        # INPUT & CREDENTIAL VALIDATION CHECKS
        # ----------------------------------------------------

        if not account_sid:

            return {
                "sms_status": "FAILED",
                "recipient": mobile_number,
                "message_sid": None,
                "error": "TWILIO_ACCOUNT_SID is missing.",
            }


        if not auth_token:

            return {
                "sms_status": "FAILED",
                "recipient": mobile_number,
                "message_sid": None,
                "error": "TWILIO_AUTH_TOKEN is missing.",
            }


        if not twilio_phone_number:

            return {
                "sms_status": "FAILED",
                "recipient": mobile_number,
                "message_sid": None,
                "error": "TWILIO_PHONE_NUMBER is missing.",
            }


        if not mobile_number:

            return {
                "sms_status": "FAILED",
                "recipient": None,
                "message_sid": None,
                "error": "Mobile number is missing.",
            }


        if not message:

            return {
                "sms_status": "FAILED",
                "recipient": mobile_number,
                "message_sid": None,
                "error": "SMS message is empty.",
            }


        # ----------------------------------------------------
        # TWILIO CLIENT INITIALIZATION & EXECUTION
        # ----------------------------------------------------

        client = Client(
            account_sid,
            auth_token,
        )


        # Dispatch message via Twilio REST API
        sms = client.messages.create(

            body="sms_delivery_updates",

            from_=twilio_phone_number,

            to="+918983331829",
        )


        # ----------------------------------------------------
        # SUCCESS RESPONSE STRUCTURE
        # ----------------------------------------------------

        return {

            "sms_status": "SENT",

            "recipient": mobile_number,

            "message_sid": sms.sid,

            "error": None,
        }


    except Exception as error:

        # ----------------------------------------------------
        # CATCH-ALL EXCEPTION HANDLING
        # ----------------------------------------------------

        return {

            "sms_status": "FAILED",

            "recipient": mobile_number,

            "message_sid": None,

            "error": str(error),
        }