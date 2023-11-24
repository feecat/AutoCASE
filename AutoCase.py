import tkinter as tk
import re
import os
from tkinter import filedialog, messagebox


class MainWindow():
    def __init__(self):
        self.tw = tk.Tk()
        self.tw.geometry("400x300")
        self.tw.title('AutoCase - by feecat')

        self.sourcefile = ''
        self.outputfile = ''

        my_font1 = ('times', 18, 'bold')
        self.l1 = tk.Label(
            self.tw, text='Automatic CASE Redistribution', width=30, font=my_font1).pack()
        self.b1 = tk.Button(self.tw, text='Select File',
                            width=20, command=self.select_file).pack()
        self.sourcefilevar = tk.StringVar()
        self.sourcefilevar.set("Please Select Source file.")
        self.w1 = tk.Label(self.tw, textvariable=self.sourcefilevar).pack()
        self.outputfilevar = tk.StringVar()
        self.outputfilevar.set("")
        self.w2 = tk.Label(self.tw, textvariable=self.outputfilevar).pack()
        self.outputfilevar2 = tk.StringVar()
        self.outputfilevar2.set("")
        self.w2 = tk.Label(self.tw, textvariable=self.outputfilevar2).pack()
        self.b3 = tk.Button(self.tw, text='Start Converter',
                            width=20, command=self.start_converter).pack()
        self.resultvar = tk.StringVar()
        self.resultvar.set("Waiting Select File.")
        self.w3 = tk.Label(self.tw, textvariable=self.resultvar).pack()
        self.tw.mainloop()

    def check_dir(self):
        if len(self.sourcefile) > 0 and len(self.outputfile) > 0 and len(self.outputfile2) > 0:
            self.resultvar.set("Waiting Start Converter")

    def select_file(self):
        self.sourcefile = filedialog.askopenfilename(
            filetypes=[("case txt", ".txt")])
        if len(self.sourcefile) > 0:
            self.sourcefilevar.set('Source File: ' + self.sourcefile)

            self.outputfile = self.sourcefile[:len(
                self.sourcefile)-4] + '_1.txt'
            self.outputfilevar.set('Output File: ' + self.outputfile)

            self.outputfile2 = self.sourcefile[:len(
                self.sourcefile)-4] + '_1.csv'
            self.outputfilevar2.set('Comment File: ' + self.outputfile2)
            self.check_dir()

    def save_file(self):
        self.outputselect = filedialog.asksaveasfile(
            initialfile=self.outputfile, filetypes=[("comment csv", ".csv")])
        if hasattr(self.outputselect, 'name'):
            self.outputfile = self.outputselect.name
            self.outputfilevar.set('Output File: ' + self.outputfile)
            self.check_dir()

    def start_converter(self):
        print('sourcefile:', self.sourcefile)
        print('savefile:', self.outputfile)
        if len(self.sourcefile) > 0 and len(self.outputfile) > 0:
            self.resultvar.set("In Processing...")
            self.tw.update()
            # Start with number, end with : not :=. like 10:
            # Only accept positive number.F
            pattern = r'^\s*\t*[0-9]\d*\s*:(?!=)'
            pattern2 = r'[0-9]\d*'  # second pattern, extract number
            pattern3 = r'//.*'  # find comment
            iNum = 0
            iTemp =0
            changetable = [[], []]
            try:
                # 1st, replace all main case number
                fo = open(self.sourcefile, mode='r')  # , encoding='UTF-8')
                fw = open(self.outputfile, mode='w')
                fw2 = open(self.outputfile2, mode='w')
                sTemp2 = 'New,Comment,Original\n'
                fw2.writelines(sTemp2)
                for line in fo:
                    # dataline = fo.readline()
                    match_result = re.findall(pattern, line)
                    if len(match_result) > 0:
                        # we got a case number, check it
                        iTemp = int(re.findall(pattern2, match_result[0])[0])
                        linechanged = False
                        if iTemp < iNum:
                            line = line.replace(str(iTemp), str(iNum))
                            changetable[0].append(iTemp)
                            changetable[1].append(iNum)
                            linechanged = True
                        else:
                            iNum = iTemp

                        comment = re.findall(pattern3, line)
                        if len(comment) > 0:
                            sTemp2 = str(iNum) + ',' + \
                                comment[0][2:] + ',' + str(iTemp) + '\n'
                            fw2.writelines(sTemp2)
                        elif linechanged:
                            sTemp2 = str(iNum) + ',' + ',' + str(iTemp) + '\n'
                            fw2.writelines(sTemp2)
                        iNum = iNum + 10

                    fw.writelines(line)
                fo.close()
                fw.close()
                fw2.close()

                # 2nd, we already have changetable, find all assignment, replace it.
                pattern = r'(?<=CASE).*(?=OF)'
                fo = open(self.outputfile, mode='r+')
                lines = fo.readlines()
                sKeyword = ''
                fo.seek(0)
                fo.truncate()
                for line in lines:
                    if len(sKeyword) == 0:
                        match_result = re.findall(pattern, line, re.I)
                        if len(match_result) > 0:
                            sKeyword = str.strip(match_result[0])
                            # match keyword assigment
                            pattern = r'(?<=' + sKeyword + \
                                r')\s*\t*:=\s*\t*[0-9]\d*(?=;)'
                    else:
                        match_result = re.findall(pattern, line, re.I)
                        if len(match_result) > 0:
                            # get number
                            iTemp = int(re.findall(
                                pattern2, match_result[0])[0])
                            # check if number in changetable
                            for index in range(len(changetable[0])):
                                if iTemp == changetable[0][index]:
                                    line = line.replace(
                                        str(iTemp), str(changetable[1][index]))
                    fo.writelines(line)
                fo.close()
                if len(sKeyword) > 0:
                    result = 'Converter Finished!'
                else:
                    result = 'Converter Failed! Cannot get KeyWord'
                self.resultvar.set(result)
            except Exception as e:
                messagebox.showerror(title='Error!', message=e)
                self.resultvar.set("Converter Failed!")
        else:
            messagebox.showwarning(
                title='Warning!', message='No file selected!')


if __name__ == "__main__":
    app = MainWindow()
