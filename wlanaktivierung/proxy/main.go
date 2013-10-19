/*
	$ go build -ldflags -s
*/
package main

import (
	"bytes"
	"log"
	"net/http"
	"regexp"

	"github.com/elazarl/goproxy"
)

var (
	reWirelessPage = regexp.MustCompile("admin/wireless.asp$")
	reTextHtml = regexp.MustCompile("text/html")
	reFilter = regexp.MustCompile("alert\\(\"WIFI function is notAvailable yet!\"\\);")
	reLocation = regexp.MustCompile("location.href = 'cable-Systeminfo.asp';")
)

type Buffer struct {
	B *bytes.Buffer
}

func NewBuffer() *Buffer {
	b := new(Buffer)
	b.B = bytes.NewBuffer([]byte{})
	return b
}

func (b *Buffer) Read(p []byte) (n int, err error) {
	return b.B.Read(p)
}

func (b *Buffer) Close() error {
	return nil
}

func main() {
	proxy := goproxy.NewProxyHttpServer()
	proxy.OnResponse().DoFunc(func(r *http.Response, ctx *goproxy.ProxyCtx) *http.Response {
		if reWirelessPage.FindString(r.Request.URL.String()) == "" ||reTextHtml.FindString(r.Header.Get("Content-Type")) == "" {
			return r
		}
		buf := NewBuffer()
		_, err := buf.B.ReadFrom(r.Body)
		if err != nil {
			log.Print(err)
			return r
		}
		
		b := reFilter.ReplaceAll(buf.B.Bytes(), []byte{})
		b = reLocation.ReplaceAll(b, []byte{})
		buf.B.Reset()
		buf.B.Write(b)
		
		r.Body = buf
		r.ContentLength = int64(buf.B.Len())
		return r
	})
	log.Fatal(http.ListenAndServe(":8080", proxy))
}
