package xStatus;

import javax.imageio.ImageIO;

import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.InetAddress;
import java.net.URL;
import java.util.*;
import java.util.concurrent.*;
import java.util.List;

@SuppressWarnings("serial")
public class Main extends JFrame {
    //private static final String FILE_PATH_1 = "C:\\Users\\Public\\Documents\\xStatus\\xSchedule.status.path.txt";
    private static final String FILE_PATH_2 = "C:\\Users\\Public\\Documents\\xStatus\\xSchedule.status.ips.txt";
    private static final String FILE_PATH_3 = "C:\\Users\\Public\\Documents\\xStatus\\xschedule.windows.properties";
    private static final String FILE_PATH_4 = "C:\\Users\\Public\\Documents\\xStatus\\controller_offline.pyw";
    private static final String FILE_PATH_5 = "C:\\Users\\Public\\Documents\\xStatus\\email_details.txt";
    private static final String FILE_PATH_6 = "C:\\Users\\Public\\Documents\\xStatus\\controller_online.pyw";
	//private static final String FILE_PATH_7 = "C:\\Users\\Public\\Documents\\xStatus\\localhostip.txt";
    
	private static final int REFRESH_TIME = 30;
    private JTextArea textArea;
    private List<String> ipAddresses = new ArrayList<>();
    private Map<String, Boolean> previousStatus = new ConcurrentHashMap<>();
    private JLabel timerLabel;
    private JLabel statusLabel;
    private ScheduledExecutorService executor;
    
    public Main() {
        setupGUI();
        createFoldersAndFiles();
        readIPsFromFile(FILE_PATH_2);
        setupExecutorService();
        startPinging();
        loadIcon();
        createPythonScriptOffline();
        createPythonScriptOnline();
        startXScheduler();
        checkWindowOpen();
    }

    private void setupGUI() {
        setLayout(new BorderLayout());
        textArea = new JTextArea();
        textArea.setEditable(false);
        timerLabel = new JLabel();
        statusLabel = new JLabel("Loading...");
        statusLabel.setHorizontalAlignment(JLabel.CENTER);
        add(new JScrollPane(textArea), BorderLayout.CENTER);
        add(timerLabel, BorderLayout.NORTH);
        add(statusLabel, BorderLayout.SOUTH);
        setSize(250, 250);
        setTitle("xStatus");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setVisible(true);
        setResizable(false);
        setAlwaysOnTop(true);
    }

    private void createFoldersAndFiles() {
        createFolder("C:\\Users\\Public\\Documents\\xStatus");
        //createFile(FILE_PATH_1);
        createFile(FILE_PATH_2);
        createFile(FILE_PATH_3);
        createFile(FILE_PATH_5);
        //createFile(FILE_PATH_7);
    }

    private void createFolder(String path) {
        File folder = new File(path);
        if (folder.mkdir()) {
            System.out.println("Folder created successfully at: " + path);
        } else {
            System.out.println("Error encountered while creating the folder or it already exists.");
        }
    }

    private void createFile(String filePath) {
        try {
            File file = new File(filePath);
            if (file.createNewFile()) {
                System.out.println("File created: " + file.getName());
            } else {
                System.out.println("File already exists.");
            }
        } catch (IOException e) {
            System.out.println("An error occurred while creating the file.");
            e.printStackTrace();
        }
    }

    private void readIPsFromFile(String fileName) {
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            while ((line = br.readLine()) != null) {
                ipAddresses.addAll(Arrays.asList(line.split(", ")));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void setupExecutorService() {
        executor = Executors.newScheduledThreadPool(2);
    }

    private void startPinging() {
        executor.scheduleAtFixedRate(() -> {
            StringBuilder sb = new StringBuilder();
            for (String ip : ipAddresses) {
                try {
                    InetAddress inet = InetAddress.getByName(ip.trim());
                    boolean reachable = inet.isReachable(5000);
                    sb.append(ip).append(" is ").append(reachable ? "reachable" : "not reachable").append("\n");

                    if (previousStatus.get(ip) != null) {
                        if (!previousStatus.get(ip) && reachable) {
                            System.out.println(ip + " is now reachable");
                            executePythonScriptOnline();
                        } else if (previousStatus.get(ip) && !reachable) {
                            System.out.println(ip + " is now not reachable");
                            executePythonScriptOffline();
                        }
                    }
                    previousStatus.put(ip, reachable);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            SwingUtilities.invokeLater(() -> textArea.setText(sb.toString()));
            startCountdown();
        }, 0, REFRESH_TIME, TimeUnit.SECONDS);
    }

    private void startCountdown() {
        for (int i = REFRESH_TIME; i >= 0; i--) {
            final int secondsLeft = i;
            SwingUtilities.invokeLater(() -> timerLabel.setText("Next refresh in " + secondsLeft + " seconds"));
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private void checkWindowOpen() {
        executor.scheduleAtFixedRate(() -> {
            try {
                String windowTitle = "xLights Scheduler";
                Process process = new ProcessBuilder("cmd.exe", "/c", "tasklist /v /fo csv | findstr /i \"" + windowTitle + "\"").start();
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                    String line;
                    boolean isOpen = false;
                    while ((line = reader.readLine()) != null) {
                        if (line.toLowerCase().contains(windowTitle.toLowerCase())) {
                            isOpen = true;
                            break;
                        }
                    }
                    final String status = isOpen ? "xSchedule is open" : "xSchedule is not open";
                    SwingUtilities.invokeLater(() -> statusLabel.setText(status));

                    if (previousStatus.get(windowTitle) != null && previousStatus.get(windowTitle) && !isOpen) {
                        Runtime.getRuntime().exec("cmd /c start \"\" /I \"C:\\Program Files\\xLights\\xSchedule.exe\"");
                    }
                    previousStatus.put(windowTitle, isOpen);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, 0, 1, TimeUnit.SECONDS);
    }

    private void loadIcon() {
        try {
            URL url = new URL("https://icon-library.com/images/status-icon/status-icon-17.jpg");
            Image image = ImageIO.read(url);
            setIconImage(image);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void createPythonScriptOffline() {
        String pythonCode = """
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email():
    try:
        # Read the SMTP server and account details from the file.
        with open('C:\\\\Users\\\\public\\\\Documents\\\\xStatus\\\\email_details.txt', 'r') as f:
            lines = f.readlines()
            
        if len(lines) < 4:
            raise ValueError("The email_details.txt file must contain at least 4 lines.")
        
        smtp_server = lines[0].strip()
        fromUsername = lines[1].strip()
        password = lines[2].strip()
        toUsername = lines[3].strip()
        smtp_port = lines[4].strip()

        # Create the message.
        msg = MIMEMultipart()
        msg['From'] = fromUsername
        msg['To'] = toUsername
        msg['Subject'] = "xStatus: Controller Offline!"
        body = "xStatus has detected a controller as offline."
        msg.attach(MIMEText(body, 'plain'))

        # Send the email.
        server = smtplib.SMTP(smtp_server, smtp_port)  # Usually 587 or 465 for SSL
        server.starttls()  # Enable TLS
        server.login(fromUsername, password)
        text = msg.as_string()
        server.sendmail(fromUsername, toUsername, text)
        server.quit()
        
    except FileNotFoundError:
        print("The email_details.txt file was not found.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    send_email()

            """;

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(FILE_PATH_4))) {
            writer.write(pythonCode);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void createPythonScriptOnline() {
        String pythonCode = """
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email():
    try:
        # Read the SMTP server and account details from the file.
        with open('C:\\\\Users\\\\public\\\\Documents\\\\xStatus\\\\email_details.txt', 'r') as f:
            lines = f.readlines()
            
        if len(lines) < 4:
            raise ValueError("The email_details.txt file must contain at least 4 lines.")
        
        smtp_server = lines[0].strip()
        fromUsername = lines[1].strip()
        password = lines[2].strip()
        toUsername = lines[3].strip()
        smtp_port = lines[4].strip()

        # Create the message.
        msg = MIMEMultipart()
        msg['From'] = fromUsername
        msg['To'] = toUsername
        msg['Subject'] = "xStatus: Controller Recovered!"
        body = "xStatus has detected a controller has come back online."
        msg.attach(MIMEText(body, 'plain'))

        # Send the email.
        server = smtplib.SMTP(smtp_server, smtp_port)  # Usually 587 or 465 for SSL
        server.starttls()  # Enable TLS
        server.login(fromUsername, password)
        text = msg.as_string()
        server.sendmail(fromUsername, toUsername, text)
        server.quit()
        
    except FileNotFoundError:
        print("The email_details.txt file was not found.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    send_email()

            """;

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(FILE_PATH_6))) {
            writer.write(pythonCode);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void executePythonScriptOffline() {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python", FILE_PATH_4);
            processBuilder.start();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void executePythonScriptOnline() {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python", FILE_PATH_6);
            processBuilder.start();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void startXScheduler() {
        try {
            Runtime.getRuntime().exec("cmd /c start \"\" /I \"C:\\Program Files\\xLights\\xSchedule.exe\"");
            TimeUnit.SECONDS.sleep(10);
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            Thread.currentThread().interrupt();
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(Main::new);
    }
}
