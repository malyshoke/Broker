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
                        Console.WriteLine($"You got a message: {m.data}");
                        Console.WriteLine($"From: {m.header.from}");
                        break;
                    default:
                        Thread.Sleep(100);
                        break;
                }
            }
        }
        static void Main(string[] args)
        {
            Console.WriteLine("Client has started");
            Thread t = new Thread(ProcessMessages);
            t.Start();

            var m = Message.send(MessageRecipients.MR_BROKER, MessageTypes.MT_INIT);
            while (true)
            {
                Console.WriteLine("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit");
                int menu;
                if (int.TryParse(Console.ReadLine(), out menu))
                {
                    switch (menu)
                    {
                        case 1:
                            {
                                Console.WriteLine("Enter receiver's id");
                                int to;
                                while (int.TryParse(Console.ReadLine(), out to) != true)
                                {
                                    Console.WriteLine("Enter number");
                                }
                                Console.WriteLine("Enter your message");
                                var str = Console.ReadLine();
                                if (str is not null & to != 0)
                                {
                                Message.send((MessageRecipients)to, MessageTypes.MT_DATA, str);
                                }
                                break;
                            }
                        case 2:
                            {
                                Console.WriteLine("Enter your message");
                                var str = Console.ReadLine();
                                if (str is not null)
                                {
                                    Message.send(MessageRecipients.MR_ALL, MessageTypes.MT_DATA, str);
                                }
                                break;
                            }
                        case 3:
                            {
                                Message.send(MessageRecipients.MR_BROKER, MessageTypes.MT_EXIT);
                                System.Environment.Exit(0);
                                break;
                            }
                    }
                }
            }
        }
    }
}
