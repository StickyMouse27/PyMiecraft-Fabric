package top.fish1000.pymcfabric;

import net.minecraft.server.MinecraftServer;
import top.fish1000.pymcfabric.executor.NamedAdvancedExecutor;

public class Py4jEntryPoint {
    public Py4jEntryPoint() {
    }

    public Utils getUtils() {
        return new Utils();
    }

    public NamedAdvancedExecutor<MinecraftServer> getExecutor() {
        return null;
    }
}
