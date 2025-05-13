package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SignInDTO {
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("password")
    private String password;
}   