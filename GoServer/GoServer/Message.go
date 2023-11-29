package main

import (
	"bytes"
	"encoding/binary"
	"io"
	"net"
	"unsafe"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/transform"
)

const (
	MT_INIT = iota
	MT_EXIT
	MT_GETDATA
	MT_DATA
	MT_NODATA
	MT_CONFIRM
	MT_GET_FROM_STORAGE
	MT_INITSTORAGE
	MT_GETLAST_PUBLIC
	MT_REST = 10
)

const (
	MR_BROKER     = 10
	MR_ALL        = 50
	MR_STORAGE    = 20
	MR_STOR       = 40
	MR_RESTSERVER = 30
	MR_USER       = 100
)

type MsgHeader struct {
	To   int32
	From int32
	Type int32
	Size int32
}

func (h MsgHeader) Send(conn net.Conn) {
	buff := new(bytes.Buffer)
	binary.Write(buff, binary.LittleEndian, h)
	conn.Write(buff.Bytes())
}

func (h *MsgHeader) Receive(conn net.Conn) {
	buff := make([]byte, unsafe.Sizeof(*h))
	_, err := conn.Read(buff)
	if err == nil {
		binary.Read(bytes.NewBuffer(buff), binary.LittleEndian, h)
	} else {
		h.Size = 0
		h.Type = MT_NODATA
	}
}

func from866(b []byte) string {
	reader := transform.NewReader(bytes.NewReader(b), charmap.CodePage866.NewDecoder())
	r, _ := io.ReadAll(reader)
	return string(r)
}

func to866(s string) []byte {
	buff := new(bytes.Buffer)
	writer := transform.NewWriter(buff, charmap.CodePage866.NewEncoder())
	defer writer.Close()
	writer.Write([]byte(s))
	return buff.Bytes()
}

type String string

func (s String) to866() []byte {
	buff := new(bytes.Buffer)
	writer := transform.NewWriter(buff, charmap.CodePage866.NewEncoder())
	defer writer.Close()
	writer.Write([]byte(string(s)))
	return buff.Bytes()
}

type Message struct {
	Header MsgHeader
	Data   string
}

func (m *Message) init(To int32, From int32, Type int32, Data string) {
	m.Header = MsgHeader{To, From, Type, int32(len(Data))}
	m.Data = Data
}

func (m Message) Send(conn net.Conn) {
	m.Header.Send(conn)
	if m.Header.Size > 0 {
		conn.Write(to866(m.Data))
	}
}

func (m *Message) Receive(conn net.Conn) int32 {
	m.Header.Receive(conn)
	if m.Header.Size > 0 {
		buff := make([]byte, m.Header.Size)
		conn.Read(buff)
		m.Data = from866(buff)
	}
	return m.Header.Type
}

var clientID int32 = 0

func MessageSend(conn net.Conn, To int32, From int32, Type int32, Data string) *Message {
	m := new(Message)
	m.init(To, From, Type, Data)
	m.Send(conn)
	return m
}

func MessageCall(To int32, Type int32, Data string) *Message {
	conn, _ := net.Dial("tcp", "localhost:12345")
	defer conn.Close()
	m := MessageSend(conn, To, clientID, Type, Data)
	m.Receive(conn)
	if m.Header.Type == MT_INIT {
		clientID = m.Header.To
	}
	return m
}
