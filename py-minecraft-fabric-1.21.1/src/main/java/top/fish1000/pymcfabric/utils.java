package top.fish1000.pymcfabric;

import java.util.List;

import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mojang.brigadier.StringReader;
import com.mojang.brigadier.exceptions.CommandSyntaxException;

import net.minecraft.command.EntitySelector;
import net.minecraft.command.EntitySelectorReader;
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

    MinecraftServer server;

    public Utils(MinecraftServer server) {
        this.server = server;
    }

    public ServerCommandSource getCommandSource(@Nullable String name) {
        ServerWorld serverWorld = server.getOverworld();
        return new ServerCommandSource(server, serverWorld == null ? Vec3d.ZERO : Vec3d.of(serverWorld.getSpawnPos()),
                Vec2f.ZERO, serverWorld, 4, "PYMC", Text.literal(name == null ? "PYMC" : name), server,
                (Entity) null);
    }

    public void sendCommand(String command, @Nullable String name) {
        server.getCommandManager().executeWithPrefix(getCommandSource(name), command);
    }

    public List<? extends Entity> getEntities(String selector) {
        try {
            EntitySelector entitySelector = new EntitySelectorReader(new StringReader(selector), true).read();
            return entitySelector.getEntities(getCommandSource(null));
        } catch (CommandSyntaxException e) {
            LOGGER.error("Syntax Error while getting entities ", e);
            return List.of();
        }
    }

    public @Nullable Entity getEntity(String selector) {
        var entities = getEntities(selector);
        if (!entities.isEmpty())
            return getEntities(selector).getFirst();
        return (Entity) null;
    }

    public static boolean isNull(Object obj) {
        return obj == null;
    }

}
