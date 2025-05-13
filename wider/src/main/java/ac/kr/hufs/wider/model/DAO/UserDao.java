package ac.kr.hufs.wider.model.DAO;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.Users;

public interface UserDao {
    Users save(Users user);
    Optional<Users> findById(String userId);
    List<Users> findAll();
    boolean existsById(String userId);
    void deleteById(String userId);
}
