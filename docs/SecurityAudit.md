# Security Report

#### File Parameters

```sh
sha256 authlog-threats.py
# Output
SHA256 (authlog-threats.py) = 29ea344f8f7aa6300a6dcb07fd7418db747437446e1f101521f9d9bf9f5d4602
```

```sh
ls -l authlog-threats.py 12601 # bytes, 12601/1024 = 12.3kb
du authlog-threats.py 28 # 512-byte blocks
```



## Executive Summary

Although the Software is using `subprocess.run(shell=True)` the only possibilities of shell injection is from the path customized by the Licensee or unauthorized access to the filesystem and directory the script resides in to modify the Software shell commands itself which is not permitted for the Licensee to do and which is not a vulnerability of the Software itself.

Please make sure to put this script in a directory not available to any networking processes and set the steps here in Remediation.



## Test Parameters

We will use a commonly available Python security tool that the Licensee may also use to verify the findings, present the security tool report, and suggest actions to lessen Risk and Impact. 

**2.1 Project Objective:** `bandit -r authlog-threats.py --format html >> BanditReport.html`

**2.2 Project Scope:** All findings are scoped to the Software having or being available to no networking components whether through the Operating System or automatic Python environment networking modules, imports, packages, or repositories loading in the scope of the Software.

**2.3 Project Schedule:**  The Software has undergone 2 Security Reviews prior to release. A new security review is conducted with any change to the logic of the Software.

**2.4 Targets:** This software is specifically made to run on OpenBSD 7.3 with Python 3.10 or greater.

**2.5 Limitations:** None. The Software is extensively tested for security in a fully operating Production environment over a period of weeks.

**2.6 Findings Summary:** The Inherent risk associated with`subprocess.run(shell=True)`was found but did not exhibit design flaws in it's use. The base shell command is set in an uncustomizable area of the Software and cannot be modified by the Licensee. The complete shell command construction contains variables for file path set by the Licensee.

**2.7 Remediation Summary:** Focus is on the surrounding Operating System protections to prevent Unauthorized modification of the Software itself.



## Findings

#### Security Tools Used

"[Bandit](https://pypi.org/project/bandit/) is a tool designed to find common security issues in Python code. To do this Bandit processes each file, builds an AST from it, and runs appropriate plugins against the AST nodes. Once Bandit has finished scanning all the files it generates a report.

Bandit was originally developed within the OpenStack Security Project and later rehomed to PyCQA."

`bandit -r authlog-threats.py --format html >> BanditReport.html`



# Test results:

[Bandit Report (HTML)](BanditReport.html)



### False Positives:

Issue: [B104:hardcoded_bind_all_interfaces] Possible binding to all interfaces.

**Explanation**

Security Review software identified IP Address `0.0.0.0` however this is not a binding or socket use but only a log search exclusion pattern used from a Regular Expression Object.

`logline = re.search(ip_pattern, line)`

**Remediation**:

Proven as a False Positive the hashtag `#nosec` was added to that line so bandit may exclude it in the future.



### Positives:

**subprocess_popen_with_shell_equals_true:** subprocess call with shell=True identified, security issue.
**Test ID:** B602
**Severity:** HIGH
**Confidence:** HIGH
**CWE:** [CWE-78](https://cwe.mitre.org/data/definitions/78.html)
**File:** [authlog-threats.py](authlog-threats.py)



# Remediation

1. Put the Software in a secure directory with no possible network access

2. Change file system group ownership of the Software to an account that is specifically for running system scripts.

3. If the Software doesn't reside in OpenBSD security checked directories such as `/root` and `/home` then manually add the directory containing the Software specifically to be checked for file permission changes.

4. Taken from [man security(8)](https://man.openbsd.org/security) System Manager's Manual

   ```sh
   Check for permission changes in special files and system binaries listed in /etc/mtree/special. 
   
   Security also provides hooks for administrators to create their own lists. These lists should be kept in /etc/mtree/ and filenames must have the suffix “.secure”. The following example shows how to create such a list, to protect the programs in /bin:
   
   # mtree -cx -p /bin -K sha256digest,type > /etc/mtree/bin.secure
   # chown root:wheel /etc/mtree/bin.secure
   # chmod 600 /etc/mtree/bin.secure
   ```

5. Set no special characters in the CUSTOMIZE area of the Software.
