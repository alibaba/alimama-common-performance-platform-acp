#include <string>
#include <vector>
class HttpRequest
{
public:
    HttpRequest(const std::string& ip, int port);
    ~HttpRequest(void);
    std::string HttpGet(std::string req);
    std::string HttpPost(std::string req, std::string data);
    static std::string genJsonString(std::string key, int value);
    static std::vector<std::string> split(const std::string &s, const std::string &seperator);
    static std::string getHeader(std::string respose, std::string key);
private:
    std::string         m_ip;
    int             m_port;
};
