package bootstrapper

import (
	"path/filepath"
	"fmt"
	"compress/gzip"
	"io"
	"os"
	"strings"
	"archive/tar"
)

func Tar(source, target string) error {
    filename := filepath.Base(source)
    target = filepath.Join(target, fmt.Sprintf("%s.tar", filename))
    tarfile, err := os.Create(target)
    if err != nil {
        return err
    }
    defer tarfile.Close()
 
    tarball := tar.NewWriter(tarfile)
    defer tarball.Close()
 
    info, err := os.Stat(source)
    if err != nil {
        return nil
    }
 
    var baseDir string
    if info.IsDir() {
        baseDir = filepath.Base(source)
    }
 
    return filepath.Walk(source,
        func(path string, info os.FileInfo, err error) error {
            if err != nil {
                return err
            }
            header, err := tar.FileInfoHeader(info, info.Name())
            if err != nil {
                return err
            }
 
            if baseDir != "" {
                header.Name = filepath.Join(baseDir, strings.TrimPrefix(path, source))
            }
 
            if err := tarball.WriteHeader(header); err != nil {
                return err
            }
 
            if info.IsDir() {
                return nil
            }
 
            file, err := os.Open(path)
            if err != nil {
                return err
            }
            defer file.Close()
            _, err = io.Copy(tarball, file)
            return err
        })
}

func Untar(tarball, target string) error {
    reader, err := os.Open(tarball)
    if err != nil {
        return err
    }
    defer reader.Close()
    tarReader := tar.NewReader(reader)
 
    for {
        header, err := tarReader.Next()
        if err == io.EOF {
            break
        } else if err != nil {
            return err
        }
 
        path := filepath.Join(target, header.Name)
        info := header.FileInfo()
        if info.IsDir() {
            if err = os.MkdirAll(path, info.Mode()); err != nil {
                return err
            }
            continue
        }
 
        file, err := os.OpenFile(path, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, info.Mode())
        if err != nil {
            return err
        }
        defer file.Close()
        _, err = io.Copy(file, tarReader)
        if err != nil {
            return err
        }
    }
    return nil
}

func Gzip(source, target string) error {
    reader, err := os.Open(source)
    if err != nil {
        return err
    }
 
    filename := filepath.Base(source)
    target = filepath.Join(target, fmt.Sprintf("%s.gz", filename))
    writer, err := os.Create(target)
    if err != nil {
        return err
    }
    defer writer.Close()
 
    archiver := gzip.NewWriter(writer)
    archiver.Name = filename
    defer archiver.Close()
 
    _, err = io.Copy(archiver, reader)
    return err
}
 
func UnGzip(source, target string) error {
    reader, err := os.Open(source)
    if err != nil {
        return err
    }
    defer reader.Close()
 
    archive, err := gzip.NewReader(reader)
    if err != nil {
        return err
    }
    defer archive.Close()
 
    target = filepath.Join(target, archive.Name)
    writer, err := os.Create(target)
    if err != nil {
        return err
    }
    defer writer.Close()
 
    _, err = io.Copy(writer, archive)
    return err
}
