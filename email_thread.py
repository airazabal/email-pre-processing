import os
import re
import string

# python package to cleanse an email. attempts to strip headers and footers. Preserves useful members:

# - original_string (original input)
# - trimmed_string (removes headers, footers, puts subject line at the top)
# - cleansed_string (removes newlines, periods, and other tokens that can be troublesome for WKS)
# - component_emails (the chunked emails representing the bodies of the various messeges in the thread)

# example usage

# example_email = EmailThread(
# email_thread = EmailThread(email_name, email_string)
# original_email = email_thread.original_string
# trimmed_email = email_thread.to_trimmed_string()
# cleansed_email = email_thread.to_cleansed_string()



### Test Variables

TEST_FROM_LINE = "From: Jim Helm [mailto:jhelm@citysigns.com] "

TEST_SENT_LINE = "Sent: Tuesday, August 08, 2017 8:10 AM"

TEST_TO_LINE = "To: Services, Agency (Comm Lines, San Antonio/SCIC)"

TEST_CC_LINE = "Cc: Evans, Sheri L (Middle Market + UW Support)"

TEST_IMPORTANCE_LINE = "Importance: High"

TEST_FORWARD_LINES = """On Mon, Aug 7, 2017 at 11:03 AM, Mate Karmi <MKarmi@karmiinsurancegroup.com> wrote:
On Thu, Dec 1, 2016 at 4:07 PM, <agency.service@thehartford.com> wrote:
On Tue, May 30, 2017 at 3:22 PM, <agency.service@thehartford.com> wrote:
On Aug 10, 2017, at 7:37 AM, Branham, Steve (ES) <Steve.Branham@adp.com> wrote:
On Tue, Jun 13, 2017 at 4:32 PM, CS-Michigan Inbox <cs-michigan@lalo.com> wrote:
On Mon, Aug 7, 2017 at 11:03 AM, Mate Karmi <MKarmi@karmiinsurancegroup.com> wrote:
---------- Forwarded message ----------
Begin forwarded message:""".split('\n')

SIGNOFF_LINES = '''Thank You
Thank you
I thank you for your time and help
Thank you
Thanks
Appreciate it
Sincerely
Thank you
Thanks
THANK YOU
Thanks for your help
Thanks & Regards
Regards
Kindest Regards
Warm Regards
Thank you
Respectfully
Thanks for your help
Best
Always a pleasure
Have a good day
have a nice day
have a great day
Regards
All the Best
Kind Regards
Take care
Many Thanks
thanks a ton
Respectfully
Respectfully yours
Very Respectfully
Sent from my
Cheers
Thanks
Talk to you later
Sent from
All Best'''.lower().split("\n")


### constants for use in program computation
## aka - standard
FORWARDED_MESSAGE_EXAMPLES = """Begin forwarded message
---------- Forwarded message ----------
_________________________________________________
Dear Partner,""".split("\n") #TODO: remove Dear Partner, put in some other alternate header type functionality

##general helper functions to debugging, etc
def printlines(lines):
    for line in lines:
        print(line)


class EmailThread():
    def __init__(self, email_id, original_string):

        ## class members
        self.email_id = None
        self.original_string = ""
        self.email_lines = []
        self.trimmed_email_lines = []
        self.component_emails = []
        self.subject = ""
        self.trimmed_email = None
        self.cleansed_email = None

        self.headers = None
        self.end_indices = None
        self.indices = None

        ## begin processing work
        self.email_id = email_id
        self.original_string = original_string
        self.email_lines = self.original_string.split("\n")
        self.initialize_subject()
        self.initialize_component_emails()
        self.remove_headers()
        self.remove_footers()
        self.create_trimmed_email()
        self.create_cleansed_email()
        #printlines(self.trimmed_email_lines)
        #print(self.trimmed_email)

    def to_trimmed_string(self):
        return self.trimmed_email

    def to_cleansed_string(self):
        return self.cleansed_email

    def initialize_subject(self):
        subject = None
        for line in self.email_lines:
            if self.is_subject_line(line):
                self.subject = line
                break
    ## tested
    def initialize_component_emails(self): ## ASSUMPTION: existence of header in the first line of the file!!
        _component_emails = []
        self.initialize_headers()
        self.initialize_end_indices()
        self.initialize_chunk_indices()
        for s, e in self.indices:
            self.component_emails.append(self.email_lines[s:e+1])
    ## tested
    def remove_headers(self):
        new_component_emails = []
        for component_email in self.component_emails:
            indices_to_remove = set()
            for i,line in enumerate(component_email):
                if self.is_from_line(line) or self.is_sent_line(line) or self.is_to_line(line) or self.is_cc_line(line) or self.is_subject_line(line) or self.is_importance_line(line) or self.is_forwarded_line(line):
                    indices_to_remove.add(i)
            new_component_emails.append([i for j, i in enumerate(component_email) if j not in indices_to_remove])
        self.component_emails = new_component_emails
    ## BUG INSIDE OF THIS - see 1490.txt
    def remove_footers(self):
        new_component_emails = []
        for q, component_email in enumerate(self.component_emails):
            signoff_indices = []
            for i, line in enumerate(component_email):
                if self.is_signoff_line(line):
                    signoff_indices.append(i)
            if len(signoff_indices) > 0:
                new_component_emails.append(component_email[0:min(signoff_indices)])
            else:
                new_component_emails.append(component_email)
            self.component_emails = new_component_emails


    def create_trimmed_email(self):
        if self.subject:
            self.trimmed_email_lines.append(self.subject)
        for component_email in self.component_emails:
            for line in component_email:
                self.trimmed_email_lines.append(line)
        self.trimmed_email = "\n".join(self.trimmed_email_lines)

    def initialize_headers(self):
        _headers = []
        for i, line in enumerate(self.email_lines):
            if self.is_from_line(line):
                _headers.append((i, line))
            elif self.is_forwarded_line(line):
                _headers.append((i, line))
        self.headers = _headers

    def initialize_end_indices(self): ## MUST be called after get_headers
        if type(self.headers) == None:
            raise Exception("must call initialize_headers first, or was an issue with initialize_headers")
        end_indices = []
        for i in range(len(self.headers)-1):
            end_indices.append(self.headers[i+1][0]-1)
        end_indices.append(len(self.email_lines)+1)
        self.end_indices = end_indices

    ## previously assumed would start with "From:" but that is not the case
    ## for all emails
    def initialize_chunk_indices(self):
        if len(self.headers) == 0:
            self.headers.append((0, "null"))
        if len(self.headers) != len(self.end_indices):
            print(self.email_id)
            print(self.headers)
            print(self.end_indices)
            raise Exception("mismatch between number of headers and end indices")
        self.indices = [(self.headers[i][0], self.end_indices[i]) for i in range(len(self.end_indices))]

    def is_from_line(self,line):
        if type(line) != str:
            raise Exception("input to _is_from_line must be a string")
        #if line[:5] == "From:" and ("mailto" in line.lower()):
        if line[:5] == "From:":
            return True
        return False

    def is_sent_line(self, line):
        if type(line) != str:
            raise Exception("input to _is_sent_line must be a string")
        if line[:5] == "Sent:":
            return True
        return False

    def is_to_line(self, line):
        if type(line) != str:
            raise Exception("input to _is_to_line must be a string")
        if line[:3] == "To:":
            return True
        return False

    def is_subject_line(self, line):
        if type(line) != str:
            exception_string = "input to _is_subject_line must be a string but is" + str(type(line)) + "\n"
            exception_string += "email id is: " + self.email_id + "\n"
            exception_string += line
            raise Exception(exception_string)
            # raise Exception("""input to _is_subject_line must be a string\n %s
            #                     lines are: %s""" % (self.email_id, exception_string))
        if line[:8] == "Subject:":
            return True
        return False

    def is_cc_line(self, line):
        if type(line) != str:
            raise Exception("input to _is_cc_line must be a string")
        if line[:3].lower() == "cc:":
            return True
        return False

    def is_importance_line(self, line):
        if type(line) != str:
            raise Exception("input to _is_importance_line must be a string")
        if line[:len("Importance:")] == "Importance:":
            return True
        return False

    def is_forwarded_line(self,line):
        if type(line) != str:
            raise Exception("input to _is_beginning_of_forwarded_message must be a string")
        if line[:2].lower() == "on" and ("wrote:" in line[-10:].lower()):
            return True
        if line[:1].lower() == "> on" and ("wrote:" in line[-10:].lower()):
            return True
        if line[:5] == "Date:":
            return True
        for forwarded_message in FORWARDED_MESSAGE_EXAMPLES:
            if forwarded_message in line:
                return True
        return False

    def is_signoff_line(self, line):
        if type(line) != str:
            raise Exception("input to _is_signoff_line must be a string")
        # line_to_test = line.lower()
        line_to_test = line.lower().strip().translate(None, string.punctuation) ## trying to match more precisely
        pattern = re.compile("\r|\n|\t|\!|,")
        line_to_test = pattern.sub("",line_to_test)
        for signoff in SIGNOFF_LINES:
            # if line_to_test[0:len(signoff)] == signoff:
            if line_to_test == signoff:
                return True
        return False

    def create_cleansed_email(self):
        ## ugly way to replace tokens we don't wan't in the email strings
        pattern1 = re.compile("\.{1,3}\s") ## remove elipses
        pattern2 = re.compile("\.\,") ## remove ., make sure to just leave the ,
        pattern3 = re.compile("\r|\n|\t|\?|\!") ## remove these random characters
        pattern4 = re.compile("\s+")
        pattern5 = re.compile(u"(\u2018|\u2019)")
        out_string = self.trimmed_email
        out_string = pattern1.sub(" ", out_string)
        out_string = pattern2.sub(",", out_string)
        out_string = pattern3.sub(" ", out_string)
        out_string = pattern4.sub(" ", out_string)
        out_string = pattern5.sub("", out_string)
        self.cleansed_email = out_string

if __name__ == "__main__":
    input_dir = "./data/blind_set_4_emails/"
    # input_dir = "./blind_set_50_emails/"
    test_files = os.listdir(input_dir)

    email_pattern = re.compile("\d\d\d\d\.txt")
    ## get just the test files from last 100 drop
    test_files = [f for f in test_files if email_pattern.match(f)]
    # test_files = ['1490.txt', '1495.txt', '1486.txt', '1549.txt', '1532.txt', '1571.txt']
    #est_files = ['1571.txt']
    # test_files = ['1611.txt']
    print("There are " + str(len(test_files)) + " files to test")

    test_files = ['9990.txt']
    for file_name in test_files:
        test_email_thread = None
        # with open ("./test_set_standard/"+file_name) as test_file:
        with open (input_dir+file_name) as test_file:
            test_file_string = test_file.read()
            print(file_name + " ************* original ************")
            print(test_file_string)
            print("************* end original ************\n\n\n")
            test_email_thread = EmailThread(file_name, test_file_string)
            print("\n\n\n *************************\ntest file \"%s\" with chunks:" % file_name)
            # printlines(test_email_thread.indices)
            print(test_email_thread.to_trimmed_string())
            print("\t\t cleansed *************************")
            # print(test_email_thread.to_cleansed_string())
            print(test_email_thread.to_cleansed_string())
            #x = raw_input()


#### OLD TESTS ####
    # TESTING_HEADER_FUNCTIONS = False
    # if TESTING_HEADER_FUNCTIONS:
    #     test_email_thread = EmailThread("1", "test_original_email_string")
    #     ## From
    #     print("Testing from line, should return True")
    #     print(test_email_thread.is_from_line(TEST_FROM_LINE))
    #     ## Sent
    #     print("Testing sent line, should return True")
    #     print(test_email_thread.is_sent_line(TEST_SENT_LINE))
    #     ## to
    #     print("Testing to line, should return True Once")
    #     print(test_email_thread.is_to_line(TEST_TO_LINE))
    #     ## cc
    #     print("Testing cc line, should return True Once")
    #     print(test_email_thread.is_cc_line(TEST_CC_LINE))
    #     ## importance
    #     print("Testing importance line, should return true once")
    #     print(test_email_thread.is_importance_line(TEST_IMPORTANCE_LINE))
    #     ## forwarded
    # TESTING_FORWARD__AND_SIGNOFF_FUNCTIONS = False
    # if TESTING_FORWARD__AND_SIGNOFF_FUNCTIONS:
    #     test_email_thread = EmailThread("1", "test_original_email_string")
    #     print("Testing forwarded Messages, should return True many times")
    #     for forward_line in TEST_FORWARD_LINES:
    #         print(test_email_thread.is_forwarded_line(forward_line))
    #     ## signoff
    #     print("Testing signoff Message, should return True many times")
    #     for signoff in SIGNOFF_LINES:
    #         print(test_email_thread.is_signoff_line(signoff))
