using System;
using System.Collections.Generic;
using System.Security.Principal;
using System.IO;

namespace BootStrap
{
    class Utils
    {
        public static void RecursiveCopy(String source, String dest)
        {
            RecursiveCopy(source, dest, true);
        }
        public static void RecursiveCopy(String source, String dest, bool overwrite)
        {
            //we need to check if the destination directory exists.
            //if not, create it.
            if (!Directory.Exists(dest))
            {
                Directory.CreateDirectory(dest);
            }

            if (!Directory.Exists(source))
            {
                throw (new DirectoryNotFoundException("The specified source directory does not exist."));
            }

            foreach (String f in Directory.GetFiles(source))
            {
                String sname = Path.Combine(dest, Path.GetFileName(f));
                File.Copy(f, sname, overwrite);
            }

            String[] directories = Directory.GetDirectories(source);
            foreach (String dir in directories)
            {
                RecursiveCopy(dir, Path.Combine(dest, Path.GetFileName(dir)), overwrite);
            }
        }
        public static bool IsAdmin()
        {
            try
            {
                WindowsIdentity identity = WindowsIdentity.GetCurrent();
                WindowsPrincipal principal = new WindowsPrincipal(identity);
                if (principal.IsInRole(WindowsBuiltInRole.Administrator))
                {
                    return true;
                }
                else
                {
                    return false;
                }
            }
            catch (Exception)
            {
                return false;
            }
        }

    }
}
