using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace BootStrap
{
    class Program
    {
        static void Main(string[] args)
        {
            String location = "";
            string ZipContents = "";
            string src = "";

            if (!Utils.IsAdmin())
            {
                MessageBox.Show("You do not have administration priviledges, exiting.", "Error!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

            int i;
            for (i = 0; i < args.Length; i++)
            {
                //we always need one lookahead:
                if (i < args.Length - 1)
                {
                    if (args[i] == "-p")
                    {
                        //we need to find the process that we are waiting to close.
                        Process[] processes = Process.GetProcessesByName(args[i + 1]);
                        if (processes.Length > 0)
                        {
                            //wait for the first process we find to exit.
                            processes[0].WaitForExit();
                        }
                    }

                    if (args[i] == "-l")
                    {
                        location = args[i + 1]; //the location was provided on the command line.
                    }
                    if (args[i] == "-d")
                    {
                        ZipContents = args[i + 1];
                    }
                }
            }


            src = Path.Combine(Environment.CurrentDirectory, ZipContents);
            Utils.RecursiveCopy(src, location, true);

        }
    }
}
