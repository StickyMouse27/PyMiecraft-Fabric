package top.fish1000.pymcfabric;

import java.util.List;

import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mojang.brigadier.StringReader;
import com.mojang.brigadier.exceptions.CommandSyntaxException;

import net.minecraft.block.BlockState;
import net.minecraft.command.EntitySelector;
import net.minecraft.command.EntitySelectorReader;
import net.minecraft.entity.Entity;
import net.minecraft.entity.MovementType;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.registry.tag.BlockTags;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.Text;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.MathHelper;
import net.minecraft.util.math.Vec2f;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.shape.VoxelShape;
import py4j.GatewayServer;
import top.fish1000.pymcfabric.executor.NamedAdvancedExecutor;

public class PymcMngr {
    public static final String MOD_ID = "py-minecraft-fabric";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    public static @Nullable NamedAdvancedExecutor<Object> executor;
    public static @Nullable GatewayServer gatewayServer;
    public static @Nullable MinecraftServer server;

    public static boolean py4jStarted = false;

    public static void tick(String name) {
        tick(name, server);
    }

    public static void tick(String name, Object data) {
        if (executor != null && py4jStarted)
            executor.tryTick(data, name);
    }

    public static ServerCommandSource getCommandSource(@Nullable String name) {
        ServerWorld serverWorld = server.getOverworld();
        return new ServerCommandSource(server, serverWorld == null ? Vec3d.ZERO : Vec3d.of(serverWorld.getSpawnPos()),
                Vec2f.ZERO, serverWorld, 4, "PYMC", Text.literal(name == null ? "PYMC" : name), server,
                (Entity) null);
    }

    public static void sendCommand(String command, @Nullable String name) {
        server.getCommandManager().executeWithPrefix(getCommandSource(name), command);
    }

    public static List<? extends Entity> getEntities(String selector) {
        try {
            EntitySelector entitySelector = new EntitySelectorReader(new StringReader(selector), true).read();
            return entitySelector.getEntities(getCommandSource(null));
        } catch (CommandSyntaxException e) {
            LOGGER.error("Syntax Error while getting entities ", e);
            return List.of();
        }
    }

    public static @Nullable Entity getEntity(String selector) {
        var entities = getEntities(selector);
        if (!entities.isEmpty())
            return getEntities(selector).getFirst();
        return null;
    }
}
