#include <stdio.h>
#include <curl/curl.h>

int main(void)
{
  CURL *curl;
  CURLcode res;

  curl = curl_easy_init();
  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, "https://example.com");
	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 1);
	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1);
	curl_easy_setopt(curl, CURLOPT_CAINFO, "../../ca-bundle/ca-bundle.crt");

    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);
    /* Check for errors */
    if(res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s\n",
              curl_easy_strerror(res));

    /* always cleanup */
    curl_easy_cleanup(curl);
  }
  WaitForSingleObject(GetCurrentProcess(), INFINITE);
  return 0;
}
