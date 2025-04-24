# AmazonOrderScraper

## How To Run 

There are 2 Version Of Scraer On Is `Playwright` And other is `Direct Api`.
Both Takes Cookies in Difrent Format 






### playwight
> python3 amazonScraper.py -c cookies.json 

\
Cookie format:
```
[
    {
        "name": "ubid-acbin",
        "value": "259-2942353-6241962",
        "domain": ".amazon.in",
        "path": "/"
    },
    {
        "name": "x-acbin", 
        "value": "al6xW31y25Ef3YdON2zQ1HbTz@@ATwfcF6CYjNzdvVB3fw6YUwAATIm46qZN3nDy",
        "domain": ".amazon.in",
        "path": "/"
    },
    {
        "name": "at-acbin",
        "value": "Atza|IwEBIAzWi7XEHROrVmWm...",
        "domain": ".amazon.in",
        "path": "/"
    }
]
```


### Direct api
>python3 AmazonScraperFromApi_V2.py -c cookies_v2.json

Cookie format:
cookies_v2.json
```
cookie = {
    "ubid-acbin": "259-2942353-6241962",
    "x-acbin": "al6xW31y25Ef3YdON2zQ1HbTz@@ATwfcF6CYjNzdvVB3fw6YUwAATIm46qZN3nDy",
    "at-acbin": "Atza|Iw *********",
}

```



[Docs](https://docs.google.com/document/d/1tBrcoOnWDOlbctTkDGvmOTAewHB1M5xstnC-hKAniiY/edit?usp=drivesdk)


## OutPut File
<img width="1679" alt="image" src="https://github.com/user-attachments/assets/5329031c-7c86-44d8-b59a-550d9e9d7012" />

## My Amazon 
<img width="759" alt="image" src="https://github.com/user-attachments/assets/545162eb-5f50-4f6d-8d7d-0531a253eb87" />
