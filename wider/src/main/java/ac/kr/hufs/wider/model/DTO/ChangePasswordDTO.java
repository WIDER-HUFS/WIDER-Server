package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChangePasswordDTO {
    @JsonProperty("current_password")
    private String currentPassword;
    @JsonProperty("new_password1")
    private String newPassword1;
    @JsonProperty("new_password2")
    private String newPassword2;
}
