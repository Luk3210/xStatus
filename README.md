# xStatus
This application sends you status notifications about your xLights show.

Only works on Windows. Sorry, I don't have access to a Mac.

Requires Java AND Python.

**Setup:**
1. Download the latest release from the releases page.
2. Make sure you have both Java and Python installed.
3. Run the file.
4. If you receive any errors, simply close them; they will be resolved soon. Once open, close everything.
5. Cut the file and paste it in `C:\Users\Public\Documents\xStatus`.
6. Input your email details into the file called `email_details.txt` in the format:
   - Line 1: smtp
   - Line 2: sender email
   - Line 3: sender password
   - Line 4: recipient email
   - Line 5: smtp port

   **Example:**
   - Line 1: smtp.office365.com
   - Line 2: sender@outlook.com
   - Line 3: sender@outlook.com's_password
   - Line 4: recipient@example.com
   - Line 5: 587

7. Add the IP addresses of your controllers into `xSchedule.status.ips.txt` and separate them by lines.
   
   **Example:**
   - Line 1: 192.168.68.123
   - Line 2: 192.168.68.124
   - Line 3: 192.168.68.125
   - Line 4: 192.168.68.126
   - Line 5: 192.168.68.127

8. Make a shortcut to the jar file if you want.
9. Launch it and you are all set!

The email scripts are made in Python 3.12 and require smtplib.
   (pip install smtplib)

I recommend testing the Python scripts individually before using. You can easily find your SMTP and port by looking it up.

If you want to monitor the show computer as well, you can download xStatus on another device and set the show computer's IP address as one of the IP addresses to monitor.
