package ac.kr.hufs.wider.config;

import javax.crypto.SecretKey;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import io.jsonwebtoken.security.Keys;

@Configuration
public class JwtConfig {
    private final String SECRET_KEY = "yourSecretKeyShouldBeLongAndSecureAndStoredInEnvironmentVariables";

    @Bean
    public SecretKey secretKey() {
        return Keys.hmacShaKeyFor(SECRET_KEY.getBytes());
    }
} 