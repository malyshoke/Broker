using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;

namespace SharpClient
{
    class Program
    {
        static void ProcessMessages()
        {
            while (true)
            {
                var m = Message.send(MessageRecipients.MR_BROKER, MessageTypes.MT_GETDATA);
                switch (m.header.type)
                {
                    case MessageTypes.MT_DATA:
                        Console.WriteLine(m.data);
                        break;
                    default:
                        Thread.Sleep(100);
                        break;
                }
            }
        }
        static void Main(string[] args)
        {
            Thread t = new Thread(ProcessMessages);
            t.Start();

            var m = Message.send(MessageRecipients.MR_BROKER, MessageTypes.MT_INIT);
            while (true)
            {
                var s = Console.ReadLine();
                if (s is not null)
                {
                    Message.send(MessageRecipients.MR_ALL, MessageTypes.MT_DATA, s);
                }
            }
        }
    }
}
