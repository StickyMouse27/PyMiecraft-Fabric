package top.fish1000.pymcfabric;

import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.minecraft.entity.Entity;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.Text;
import net.minecraft.util.math.Vec2f;
import net.minecraft.util.math.Vec3d;

public class Utils {
    public static final String MOD_ID = "py-minecraft-fabric";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    public static ServerCommandSource getCommandSource(MinecraftServer server, @Nullable String name) {
        ServerWorld serverWorld = server.getOverworld();
        return new ServerCommandSource(server, serverWorld == null ? Vec3d.ZERO : Vec3d.of(serverWorld.getSpawnPos()),
                Vec2f.ZERO, serverWorld, 4, "PY4J", Text.literal(name == null ? "PY4J" : name), server, (Entity) null);
    }

}
