package main

import (
	"io"
	"fmt"
	"bytes"
	"log"
	"net/http"
	"time"
	"regexp"
	"net/url"
	"runtime"

	"github.com/elazarl/goproxy"
	"github.com/toqueteos/webbrowser"
)

const (
	PROXY = "192.168.0.1"
)

var (
	activeWls = []byte("var WlsStatus=\"1\";")
	reAdminUrl = regexp.MustCompile("/admin/[^\\.]+\\.asp$")
	reWlsStatus = regexp.MustCompile("var WlsStatus=\"\";")
	httpClient *http.Client
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

func proxyHandler(r *http.Response, ctx *goproxy.ProxyCtx) *http.Response {	
	if reAdminUrl.FindString(r.Request.URL.Path) == "" {
		return r
	}

	buf := NewBuffer()
	_, err := buf.B.ReadFrom(r.Body)
	if err != nil {
		log.Print(err)
		return r
	}
	
	b := reWlsStatus.ReplaceAll(buf.B.Bytes(), activeWls)
	buf.B.Reset()
	buf.B.Write(b)
	
	r.Body = buf
	r.ContentLength = int64(buf.B.Len())
	return r
}
	
func handler(w http.ResponseWriter, r *http.Request) {
	r.Host = PROXY
	u, _ := url.Parse("http://" + r.Host + r.RequestURI)
    r.URL = u
	r.RequestURI = ""
	resp, err := httpClient.Do(r)
	if err != nil {
		log.Print(err)
	}
	defer resp.Body.Close()
	for key, values := range resp.Header {
		for _, value := range values {
			w.Header().Add(key, value)
		}
	}
	io.Copy(w, resp.Body)
}
	
func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())

	proxy := goproxy.NewProxyHttpServer()
	proxy.OnResponse().DoFunc(proxyHandler)
	go func() {
		err := http.ListenAndServe(":8080", proxy)
		if err != nil {
			log.Fatal(err)
		}
	}()
	go func() {
		time.Sleep(time.Second * 1)
		webbrowser.Open("http://localhost:8081/admin/cable-Systeminfo.asp")
	}()
	proxyUrl, _ := url.Parse("http://localhost:8080/")
	httpClient = &http.Client{Transport: &http.Transport{Proxy: http.ProxyURL(proxyUrl)}}
	http.HandleFunc("/", handler)
	log.Fatal(http.ListenAndServe(":8081", nil))
}
